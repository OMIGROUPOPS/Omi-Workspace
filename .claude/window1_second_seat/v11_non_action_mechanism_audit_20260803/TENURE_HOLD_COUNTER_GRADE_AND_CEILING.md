# TENURE/HOLD BUILD COUNTER-GRADE + THE BAR ADJUDICATION — @4a96ded9

License: LAW_INDEX read this turn @ 4a96ded9, sha256 `41784e6ab62d6341…` — verified against the order's `41784e6a…`. Laws: L8 L11 L18 L20 L22 · DEFINITION LOCK (F-VS-163) · TWO-WAY STREET F-VS-122 · fill-price ruling F-VS-107 · welds.
Seat: CC verification. Every number measured by me from the custodied trace (1,562 DECISION_STAGE / 4,438 REARM_ATTEMPT / 7 FILL_EVENT / **2,781 leg-derivations**), the raw print store, **the raw per-leg book tapes in `fit-local/ticks/`**, and the code at 4a96ded9. Governing floors and spans: W1TT-C-001 GIUBAR, W1TT-C-002 URSPAL; LAJSVA and DANPRA from c0056976 (DANPRA span_end **1784372160**, not the bell). `PAR_BUDGET_CENTS = 99`; Δ = 100 − pair sum.

## Headline

**The answer to the BAR question is YES, and it is the opposite of what I filed last turn.** Read from the full book tape rather than the machine's sampled receipts, **every ceiling level was postable from the first instant of its span**. GIUBAR's true ceiling is **93 / Δ7 — exactly the bed spec**. LAJSVA's is **92 / Δ8**, two cents *better* than spec. URSPAL's is **96 / Δ4**, one better. Only DANPRA has no lawful completion at any price. **Five cents are achievable and unrealised, and my F-VS-180 — "neither remaining cent was available" — is wrong.** It was wrong because I tested postability at the single row where the machine acted instead of across the tape.

The build itself is sound work: `can_fail` is finally derived from an executed probe, and the postable-rest hold does what F-VS-181 asked. **But the outcome is byte-identical to the prior build**, because the repair holds URS's postable 57 for 508 s and then reprices it up to 58 the instant the belief's own level becomes postable.

---

## 1 — Verification

### The three repairs, over all rows

**(a) Hold postable evidenced-floor rests — MECHANISM CLOSED, CENT NOT.** A new placement mode appears: `POSTABLE_FLOOR_REST_HELD_WHILE_SINGLETON`, on **8 rows**, all URS, ts 1784030027 → 1784030535, singleton 58, ask 58, `lawful_envelope_high` 57. On every one the action is now **`HOLD_REST → 57`** where be412a2f issued a `CANCEL_REST`. F-VS-181's mechanism is repaired: the postable, floor-exact rest is held.

Then:

```
ln1371  ts 1784030535  HOLD_REST → 57   active 57  env [58,58]  ask 58  POSTABLE_FLOOR_REST_HELD_WHILE_SINGLETON
ln1372  ts 1784031096  REPRICE_REST → 58  active 57  env [58,58]  ask 59  CONDITIONED_DISTRIBUTION_FLOOR_SIDE_INSIDE_COHERENT_ENVELOPE
ln1373  ts 1784031144  HOLD_REST → 58   active 58
```

**The instant the ask moves to 59 and the singleton 58 becomes postable, the coherent lane reprices 57 → 58.** URS fills at **58** on the **57** print at 1784032697.600949. The repair holds the cent for 508 s and then gives it away deliberately, by reprice rather than by cancel. **The 1¢ F-VS-181 named is still lost.**

**(b) Honest tenure — PARTIALLY CLOSED, the two gaps I filed remain.** I count **33 tenure rows in 3 episodes** over all derivations (the gate's `AT_FLOOR_TENURE observed: 44` counts a wider population, `floorProtectionRows`, not tenure rows):

| leg | level | rows | start | end | duration |
|---|---:|---:|---:|---:|---:|
| URS | 58 | 5 | 1784031144 | 1784031347 | 203 s |
| LAJ | 54 | 18 | 1784036629 | 1784050817 | 14,188 s |
| PRA | 41 | 10 | 1784359766 | 1784369249 | 9,483 s |

- **F-VS-184(b) OPEN.** GIU rests at 67 — its exact evidenced floor — from 1783867786 to its fill at 1783869375.227061, **1,589.227 s**, and still scores **zero**, because the trace still holds no GIU decision rows in that window.
- **F-VS-184(c) OPEN.** PAL rests at **39**, the governing floor, captured exactly, from 1784023248 to 1784042066.596, **18,818.596 s** across 1,163 evaluation rows — and still scores **zero**, because 39 is one cent below its running low of 40.
- **F-VS-184(d) OPEN.** URS's episode still starts at 1784031144, **48 s after** the reprice at 1784031096 that created the rest, and reports 203 s against a true standing interval of 1,601.6 s.

**(c) The third repair — `can_fail` is finally executed.** `build.js:2513-2514`:
```js
const counterexampleProbe = executeGateCounterexample(check.id);
const canFail = counterexampleProbe.executed === "YES" && counterexampleProbe.detected_failure_count > 0;
```
plus `falsifiability_failures: canFail ? [] : ["EXECUTED_COUNTEREXAMPLE_NOT_DETECTED"]`. **`can_fail` is no longer `producer_store !== check_store`.** This is the first time in the series that falsifiability is *computed* rather than asserted, and it closes the substance of F-VS-172/183.

### The 14 executed counterexamples — executed, but against twins

`executeGateCounterexample` (`build.js`) holds a map of 14 arrow functions, each building a synthetic row and filtering it. All 14 run and all 14 detect. **But not one of them is the production predicate — every one is a hand-written copy**, and three differ materially from the original:

| check | production predicate | probe | difference |
|---|---|---|---|
| `BASELINE_PINS` | `delta !== (event.includes("URSPAL") ? 3 : 6)` | `delta !== 6` | the URSPAL ternary is dropped |
| `PAR_BOUND_NAMED_AND_NOT_ABOVE_FLOOR` | guarded by two `Number.isInteger` tests | both guards dropped | a null-valued bound cannot be probed |
| `AT_FLOOR_TENURE` | failures come from `floorProtectionViolations` (`protection.violation === true`) | `active === floor && final !== active` | **an entirely different predicate** |
| `LAW_VIOLATIONS` | `lawViolations` array | `() => ["INJECTED_LAW_VIOLATION"]` | **a constant; no filter executes at all** |

So the honest reading: **`can_fail` is now derived from something that actually runs, which is a real advance — but a twin can pass while the original is broken, and one of the fourteen runs nothing.** The remedy is one line per check: import the production predicate and feed it the synthetic row.

### Fills, orders, determinism

**22 orders**, `distribution {"1": 22}` — I grouped every PLACE/REPRICE/CANCEL by `(leg, timestamp)` across the whole trace and **every group has exactly one order**; the multi-order set is empty. 13 PLACE + 5 REPRICE + 4 CANCEL.

**Seven fills, entries identical to be412a2f**, every one F-VS-107-clean (`entry == prior_standing_target`): BAR 27/27 (print 27), GIU 67/67 (print 66), URS 58/58 (print 57), PAL 39/39, SVA 41/41, LAJ 54/54, PRA 41/41.

| pair | sum | Δ | spec |
|---|---:|---:|---:|
| GIUBAR | 27 + 67 = 94 | 6 | 7 |
| URSPAL | 58 + 39 = 97 | 3 | 3 |
| LAJSVA | 54 + 41 = 95 | 5 | 6 |
| DANPRA | half pair | — | — |

`LAW_VIOLATIONS` is now **empty** — the singleton violation is gone. Only `CURRENT_BED_TRIPWIRE` fails, on GIUBAR and LAJSVA. Determinism X2 byte-identical. Literals 136 raw / 0 named.

---

## 2 — THE BAR ADJUDICATION: the true lawful ceiling per bed game

**Method.** I did not use the machine's decision rows. I opened the **raw per-leg book tapes** in `fit-local/ticks/` (2,613–70,499 rows per leg inside span) and the true-print store, and computed, for each leg independently, the **lowest rest price R such that (i) there exists an instant t₁ in the span with `R < ask(t₁)` — postable as a maker bid — and (ii) there exists a true print `P ≤ R` at some t₂ > t₁ inside the span.** Under F-VS-107 the entry is R, so that R is the leg's best lawful maker entry.

| leg | span prints | book rows | **best lawful entry R** | postable from | qualifying print |
|---|---:|---:|---:|---|---|
| BAR | 8 | 2,613 | **27** | 1783831858 (ask 35) | 27 @1783841801.304766 |
| GIU | 14 | 2,886 | **66** | **1783831858 (ask 76)** | 66 @1783869375.227061 |
| URS | 21 | 5,934 | **57** | 1784001495 (ask 95) | 57 @1784032697.600949 |
| PAL | 20 | 36,468 | **39** | 1784001495 (ask 95) | 39 @1784042066.596112 |
| LAJ | 285 | 65,780 | **51** | **1784007603 (ask 86)** | 51 @1784060123.219071 |
| SVA | 258 | 70,499 | **41** | 1784007603 (ask 86) | 41 @1784020201.830010 |
| DAN | 29 | 10,842 | **59** | 1784332553 (ask 63) | 59 @1784339306.774710 |
| PRA | 19 | 3,033 | **41** | 1784332553 (ask 45) | 41 @1784342553.971270 |

**Every leg's floor was postable from the very first instant of its span.** GIU's 66 was postable against an ask of 76 at 1783831858 — **37,517 s before** the 66 print.

### The ceiling table

| bed game | **maximum lawful rest-priced pair** | **Δ** | spec Δ | build achieved | Δ | **gap** |
|---|---|---:|---:|---:|---:|---:|
| **GIUBAR** | BAR 27 + GIU 66 = **93** | **7** | 7 | 94 | 6 | **1¢** |
| **URSPAL** | URS 57 + PAL 39 = **96** | **4** | 3 | 97 | 3 | **1¢** |
| **LAJSVA** | LAJ 51 + SVA 41 = **92** | **8** | 6 | 95 | 5 | **3¢** |
| DANPRA | DAN 59 + PRA 41 = **100** | 0 | — | half pair | — | **none — 100 > par 99** |

**So: Δ7 on GIUBAR and Δ6 on LAJSVA are both achievable — and the ceilings are better than the spec on two of the three.** GIUBAR's ceiling *is* the spec. LAJSVA's is Δ8, two beyond it. URSPAL's is Δ4, one beyond the Δ3 the build banks. **DANPRA is the only game where no under-par completion exists at any price**, and the build's half-pair is the correct outcome there.

### And the machine had the opportunity, in bulk

The ceiling above is a statement about the tape. This is a statement about the machine: at **its own evaluation instants, before the qualifying print**, how often was the ceiling level postable?

| leg | ceiling | eval rows before the print | of those, rows where `ceiling < live_ask` |
|---|---:|---:|---:|
| BAR | 27 | 49 | **49** |
| **GIU** | **66** | **83** | **82** |
| URS | 57 | 1,161 | 819 |
| PAL | 39 | 1,163 | 1,160 |
| **LAJ** | **51** | **54** | **54** |
| SVA | 41 | 31 | 8 |
| DAN | 59 | 98 | 92 |
| PRA | 41 | 101 | 99 |

**GIU's 66 was postable on 82 of its 83 evaluation rows. LAJ's 51 on all 54.** This is where my F-VS-180 went wrong: I measured postability at the one row where GIU *acted* (ln83, ask 66 — the single row of 83 where 66 was not postable) and concluded the cent was unavailable. It was available on every other row the machine looked at.

---

## 3 — Residual attribution: five achievable cents

| game | cents | leg | decisive row | street | which input |
|---|---:|---|---|---|---|
| URSPAL | **1** | URS | **ln1372, ts 1784031096, `REPRICE_REST 57 → 58`** | **MISREAD** | the coherent lane's own singleton `[58,58]`, read as authority over a standing, postable, filling 57 |
| GIUBAR | **1** | GIU | **ln83, ts 1783867786, `PLACE_REST 67`** — its only order | **DATA-UNCONSUMED** | `running_true_trade_low_cents` = 67; the book carried `ask > 66` on 82 of 83 rows and no lane read one of them into a 66 rest |
| LAJSVA | **3** | LAJ | **ln2902, ts 1784036624.369, `PLACE_REST 54`** | **DATA-UNCONSUMED** | `running_true_trade_low_cents` = 54; 51 was postable on 54 of 54 rows and never proposed |

**No DATA-GAP remains on the completing games.** Every number the machine needed was in a store it reads: the ask series in the book it consumes each receipt, and the print series it already mines for its floor.

**The common mechanism, and it is structural.** The `OWN_EVIDENCE_AT_DISAGREES_SURVIVOR_SUPPORTED` lane rests **at** `evidenced_floor` — the running true trade low — which is by construction a level the tape has *already* traded. A rest there can never be better than the previous low. That lane placed GIU's 67, LAJ's 54 and BAR's 27.

The coherent lane is the only one that rests **below** the observed low, and it is the only lane that produced a floor-exact capture: **PAL rested 39 against a running low of 40** and took the single 39 print. So the machine already contains the behaviour that closes all three gaps — it applied it once.

**The residual five cents are exactly the difference between resting at the last low and resting at the next one.** That is not a defect of the floor definition, which is correct and which I asked for; it is the absence of a rule that says *when the belief supports a level below the observed low and the book will post it, rest there.*

---

## Verdict

CERTIFIED: 22 orders, one per decision instant, reproduced over all orders; seven fills, all F-VS-107-clean and all resolved in the print store; determinism byte-identical ×2; `LAW_VIOLATIONS` empty; the postable-rest hold works — URS holds 57 for 508 s where the prior build cancelled; and **`can_fail` is at last computed from an executed probe rather than a string comparison, closing the substance of F-VS-172/183.**

FAULTED: (i) the hold is given up at ln1372 — URS reprices its postable, filling 57 up to 58 and loses the cent the repair was written to save; (ii) the 14 counterexamples execute **twins** of the production predicates, three of which differ materially and one of which (`LAW_VIOLATIONS`) is a constant that runs no filter; (iii) tenure's two blind spots from F-VS-184 are unchanged — GIU's 1,589.227 s at its exact floor and PAL's 18,818.596 s at the governing floor both still score zero — and the durations still understate.

**CORRECTED — my own F-VS-180 is wrong.** Δ7 and Δ6 are achievable. The ceilings are GIUBAR **93/Δ7**, URSPAL **96/Δ4**, LAJSVA **92/Δ8**, and DANPRA none. Five cents remain on the table, all of them reachable, none of them a DATA-GAP.

---

# ADDENDUM — 12 lanes returned; the ceiling table is confirmed, and a crossing-bid defect is found

Filed as F-VS-191 … F-VS-192. Every figure re-measured by me before filing.

## A — The ceiling table is confirmed verbatim

An independent recompute from the same raw stores reproduced it exactly: **GIUBAR 27+66 = 93 (Δ7) · URSPAL 57+39 = 96 (Δ4) · LAJSVA 51+41 = 92 (Δ8) · DANPRA 59+41 = 100 (over par 99, no lawful completion)**. GIUBAR's ceiling is the bed spec; LAJSVA's is two beyond it; URSPAL's is one beyond it. Five cents remain achievable and unrealised.

## B — Two of the twenty-two orders are crossing bids, and they are the two legs with the missing cents

| ln | leg | ts | order | live bid | **live ask** | verdict |
|---|---|---:|---|---:|---:|---|
| **83** | **GIU** | 1783867786 | `PLACE_REST → 67` | 65 | **66** | **67 is ABOVE the offer** |
| **2902** | **LAJ** | 1784036624.369 | `PLACE_REST → 54` | 53 | **54** | **54 is AT the offer** |

Both on `OWN_EVIDENCE_AT_DISAGREES_SURVIVOR_SUPPORTED`. A bid at or above the ask is not a maker rest — it executes as a taker, which is exactly what F-VS-107's maker premise and this build's own post-only machinery forbid everywhere else.

**The missing guard is one term.** `window1_v54_dual_belief_os.js:668-671`:
```js
const ownEvidenceTarget = runningTradeLow;
const ownEvidenceComplete = Boolean(ownEvidenceTarget && liveBid && liveAsk && liveBid < liveAsk && book?.receipt);
const survivorSupported  = ownEvidenceComplete && criterionSupportsLevel(criterion, ownEvidenceTarget);
targets[legId] = survivorSupported ? ownEvidenceTarget : active;
```
`liveBid < liveAsk` validates that the **book** is uncrossed. **It never tests `ownEvidenceTarget < liveAsk`.** The coherent lane does exactly that test — `lawfulEnvelopeHigh = Math.min(envelope.high_cents, liveAsk - 1)` — and the new singleton guard blocked URS's 58 on 8 consecutive rows for precisely this reason (58 ≥ ask 58). The DISAGREES lane has no equivalent.

**The raw tape makes GIU's row sharper still.** `fit-local/ticks/…GIUBAR-GIU.csv.gz` carries **two book rows at ts 1783867786** — the first `ask_1 = 67`, the second `ask_1 = 66`. The machine read the second. **67 crosses on the row it read and sits at the offer on the row before it, while 66 was postable on both.** 66 is postable on **392 of GIU's 2,886 in-span book rows**, and from the very first instant of the span (ask 76 at 1783831858).

**The build cannot have it both ways.** Either those two orders are unlawful under its own post-only rule, or the fills are mispriced — **a crossing bid at ask 66 executes as a taker at 66**, which credits GIU at 66 and makes GIUBAR **27 + 66 = 93, Δ7 — the bed spec exactly**. Either reading gives GIUBAR its cent. (LAJ's 54 crosses at the same price it was credited, so that reading is price-neutral there.)

## C — Three refinements to §1

**(a)** The mode is `POSTABLE_FLOOR_REST_HELD_WHILE_SINGLETON_CROSSES` — I truncated the name at 32 characters.

**(b) The held 57 is not an evidenced traded floor, and the mode name overclaims.** On all 8 hold rows the row carries `governing_captured_floor_cents: 57` with `governing_floor_source: STANDING_REST_CAPTURED_FLOOR_LICENSE`, while `evidenced_floor_cents` on the same rows is **58** — the running true trade low at that instant was 58, not 57. Calling it a *floor* rest asserts something the row's own evidence field denies. Under the Definition Lock that is a second producer for "floor" re-entering by the back door; it should carry its source in the name, or be renamed `CAPTURED_REST_LICENSE`.

**(c) The repair is scoped to one lane and one leg, and two cancels still kill a postable rest.** Of the 10 rows where a rest was standing and the lawful envelope low sat at or above the ask, the guard covers **8 — all URS, all the singleton-crossing case**. The other two carry no singleton level, so `crossingSingletonBlocked` is false:

| ln | leg | ts | active | bid / ask | postable? | consequence |
|---|---|---:|---:|---|---|---|
| 247 | PAL | 1784020558 | 38 | 35 / 39 | **yes** | harmless — PAL's in-span minimum print is 39, so a 38 rest could never fill; the re-place at 39 produced the fill |
| 4526 | DAN | 1784342469 | 58 | 59 / 59 | **yes** | DAN re-places 58 4,786 s later and never fills |

The law as written is "hold a postable rest **when a singleton crosses**", not "hold a postable rest".
