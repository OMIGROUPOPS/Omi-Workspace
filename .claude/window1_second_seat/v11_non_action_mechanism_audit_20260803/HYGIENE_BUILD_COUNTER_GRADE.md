# HYGIENE BUILD COUNTER-GRADE — @be412a2f

License: LAW_INDEX read this turn @ be412a2f, sha256 `41784e6ab62d6341…` — verified against the order's `41784e6a…`. Laws: L8 L11 L18 L20 L22 · DEFINITION LOCK (F-VS-163) · TWO-WAY STREET F-VS-122 · welds.
Seat: CC verification. Every number measured by me from the custodied trace (1,556 DECISION_STAGE / 4,982 REARM_ATTEMPT / 7 FILL_EVENT / **2,769 leg-derivations**), the raw print store, and the code at be412a2f. Governing floors: W1TT-C-001 GIUBAR, W1TT-C-002 URSPAL; LAJSVA and DANPRA from c0056976. `PAR_BUDGET_CENTS = 99`; Δ = 100 − pair sum.

## Headline

**Three completions, seven fills, twenty-three orders.** BAR and GIU both fill for the first time in this series. The thrash I filed as F-VS-176 is gone — 309 orders → 23, zero multi-order instants. The live-bid default is gone from the DISAGREES lane — 214 of 214 → **0 of 3**. The 17 named literals are gone — I count zero survivors. **The two remaining cents were not available**: GIU's 66 was un-postable at the only instant the machine was awake, and LAJ's 53 sat below its own observed traded low at every instant it could have been placed. **And the "LAJ rearm pending at the edge" does not exist — the trace shows it resolved; the receipt reads the wrong row class.**

---

## 1 — Verification

### The three completions, by trade_id

Seven `FILL_EVENT` rows. Every `captured_at_receipt` resolves in `fit-local/prints.jsonl`, every one `true_print: true`, and **F-VS-107 holds on all seven — `entry_cents == prior_standing_target_cents` without exception**:

| leg | trade_id | entry | rest | print | epoch (prints.jsonl) |
|---|---|---:|---:|---:|---|
| **BAR** | `4fa381b8…` | **27** | 27 | 27 | 1783841801.417152 |
| **GIU** | `924208a2…` | **67** | 67 | 66 | 1783869375.227061 |
| URS | `a4575e0c…` | 58 | 58 | 57 | 1784032697.600949 |
| PAL | `11b32855…` | 39 | 39 | 39 | 1784042066.596112 |
| SVA | `62c5acca…` | 41 | 41 | 41 | 1784020209.484174 |
| LAJ | `16abd619…` | 54 | 54 | 54 | 1784050973.062825 |
| PRA | `6a5b1a68…` | 41 | 41 | 41 | 1784369249.287716 |

| pair | sum | Δ | spec | verdict |
|---|---:|---:|---:|---|
| **GIUBAR** | 27 + 67 = **94** | **6** | 7 | completes, 1¢ short of spec |
| **URSPAL** | 58 + 39 = **97** | **3** | 3 | completes, **meets spec** |
| **LAJSVA** | 54 + 41 = **95** | **5** | 6 | completes, 1¢ short of spec |
| DANPRA | PRA 41 filled, DAN resting 58 | — | — | half pair; 59+41 = 100 against par 99, no under-par offer exists |

**BAR's placement is the sharpest row in the run.** `ln49, ts 1783841801.304` — `PLACE_REST → 27` at the microsecond of the 27 print (1783841801.304766), on `OWN_EVIDENCE_AT_DISAGREES_SURVIVOR_SUPPORTED` with the live bid at 25 and `evidenced_floor 27`. The next 27 print, 112 ms later, took it. Where every prior build chased the bid down to 25/26 and missed by 29.3 s, this one stands at the traded floor the instant the floor exists.

### The 23-order arbitration — reproduced over ALL orders

I counted every `PLACE_REST` / `REPRICE_REST` / `CANCEL_REST` in the trace: **13 PLACE + 5 REPRICE + 5 CANCEL = 23**, and grouped them by `(leg_id, timestamp_epoch)` across the whole trace, not a filtered set. **Every group has exactly one order. The set of multi-order instants is empty.** `distribution {"1": 23}` reproduces.

Against 453296b7: **309 orders, 62 multi-order instants, maximum 10 on one leg at one instant.** Per-leg then → now: PAL 224 → 3, URS 35 → 3, LAJ 21 → 4, SVA 9 → 3, GIU 8 → 1, BAR 5 → 1, DAN 3 → 4, PRA 4 → 4 (309 → 23). **F-VS-176 is repaired.**

The mode census shows where the orders went: `OWN_EVIDENCE_AT_DISAGREES_SURVIVOR_SUPPORTED` **332 → 22 rows**, and the coherent lane holds 2,302 of 2,769. The DISAGREES lane no longer competes for the same receipt — it acts three times in the entire run, and each time it is the winner of an arbitrated instant.

### The zero-live-bid claim — re-measured exactly as I measured 218/289

| lane | PLACE/REPRICE | `target == live_bid` |
|---|---:|---:|
| `OWN_EVIDENCE_AT_DISAGREES_SURVIVOR_SUPPORTED` | 3 | **0** |
| `CONDITIONED_DISTRIBUTION_FLOOR_SIDE_INSIDE_COHERENT_ENVELOPE` | 15 | 5 |
| **total** | **18** | **5 (28 %)** |

At 453296b7 this was **218 of 289 (75 %), including 214 of 214 on the DISAGREES lane**. The three DISAGREES orders now are BAR 27 (bid 25), GIU 67 (bid 65), LAJ 54 (bid 53) — **none at the bid**. Across all rows carrying a chosen target, `chosen == bid` on 508 of 1,583.

The check's escape hatch is honest. `envelope_placement.live_bid_relation` is `REFERENCE_ONLY_NOT_LEVEL_AUTHORITY` on 212 rows and `EVIDENCED_TRADE_LOW_HAPPENS_TO_EQUAL_LIVE_BID` on **10** — and on **all 10** the evidenced floor genuinely equals the live bid (LAJ, `bid 54 / evidenced_floor 54`, every row a HOLD). **Zero rows carry that stamp while the floor differs from the bid.** The label is not being used to excuse a default.

### The 131-literal audit

`literalClaimAudit` (`build.js:178-215`) scans four files for `field: true|false`. **I ran my own scan over the same four files at be412a2f and count exactly 131** — matching `raw_literals: 131`. **And none of the 17 F-VS-167/177 named claims survives as a literal: zero.** `same_receipt_write_then_read_removed` and `live_bid_is_reference_only` are both gone from the source. **F-VS-177(a) is repaired.**

One caveat on the audit's own reasoning, not on its count. A literal is classified `OPERATIONAL_CONTROL_OR_BRANCH_RESULT` if its field is in a four-name allowlist **or the source line matches `/return\s+\{/`, `/\?\s*\{/`, or `/:\s*\{/`** (`build.js:193-195`). In a file where receipts are written as long single-line object literals, `: {` matches almost any line. The 131 are declared explained **by line-shape, not by derivation**. The count is honest; the classifier is a proxy.

### 61/61 receipt producers

`RECEIPT_PRODUCER_COVERAGE.json`: 61 artifacts, **61 regenerable, `unproduced: []`** — reproduces. And **F-VS-178's orphan is genuinely closed**: `DEFINITION_REPAIR_SUMMARY.json` is still committed and now has a real writer at `build.js:2416` (`writeJson(path.join(output, "DEFINITION_REPAIR_SUMMARY.json"), …)`).

The method is weaker than the result: `producers = producerSources.filter((source) => source.text.includes(name))` (`build.js:237`) — a **basename substring search** in two files. A receipt merely named in a comment or a string array would pass. It happens to be sound here because I checked the one artifact that failed before.

### Floor check coverage

`FLOOR_IS_OBSERVED_TRADE_LOW_ALL_ROWS`: `{tested: 2769, total: 2769, no_trade_rows: 279}`. **`tested == total` — the 279 null-floor rows are now inside the population**, classified `NO_TRUE_TRADE_YET` and compared null-against-null rather than skipped. **F-VS-177(b) is repaired**, and the check's `counterexample_condition` says so explicitly: *"including null-vs-null rows before the first print."*

### Determinism and custody

`DETERMINISM_RECEIPT.json`: `runs_per_game: 2`, `all_byte_identical: true` on all four games. Replay stability on one tape and one host, not cross-machine. **One stale field:** the receipt's `label` still reads `V54_DEFINITION_REPAIR_DETERMINISM_X2` while the run's `run_source` is `V54_LITERALS_ONE_ORDER_UNGUARDED_20260824` — a leftover from the prior build.

Custody: 9 manifest entries, **6 verified byte-exact on disk**; the three unresolvable are `FOUNDATION_PER_MINUTE_UNIVERSE` (POSIX path) and the two survivor libraries (github URLs at 189eaa20, which I verified in the local object store at F-VS-171). `oversized_artifacts_moved_to_external_custody: 6` matches the six local files. Reconciled.

### The one thing that did not change

**`can_fail` is still `check.producer_store !== check.check_store`** (`build.js:2396`) — the same string comparison I filed as F-VS-172. The new `counterexample_condition` field appears on 8 of the 14 checks and is genuinely useful prose, but it is **not read by any predicate**: it does not participate in computing `can_fail`, `passed`, or `failures`. `gate_fields_that_can_fail: 14` remains a count of 14 non-identical label pairs.

---

## 2 — The last cents, two-way attributed

### GIUBAR Δ6 vs Δ7 — the cent is GIU's, and it was not available

GIU's whole lifecycle is one order: **`ln83, ts 1783867786, PLACE_REST → 67`**, live bid 65, **live ask 66**, `evidenced_floor 67`, sibling BAR committed at 27. The 66 print at 1783869375.227 took it at 67.

Δ7 requires GIU at 66 (27 + 66 = 93). At the receipt where GIU acted, **`66 < ask` is false — the ask WAS 66.** A maker bid at 66 sits at the offer and executes as a taker, which F-VS-107's maker premise forbids and the post-only guard blocks.

And there was no second look: **GIU has exactly one derivation in the entire window [1783867786, 1783869380]**. The machine was awake once between placing and filling, and at that instant the book denied the level.

**Attribution: not a miss, and not a street.** The tape did not offer the cent at a moment the machine could lawfully have stood there. What is worth naming is the *attention* gap — one evaluated instant across a 1,589 s window — but on the evidence the leg had, 67 was the correct and only postable level, and it captured.

### LAJSVA Δ5 vs Δ6 — the cent is LAJ's, and it required a forecast

LAJ places **54 at ln3440, ts 1784036624.369** (bid 53, ask 54, `evidenced_floor 54`) and fills at 54 at 1784050973.062825. Δ6 requires LAJ at 53 (53 + 41 = 94).

I tested all three conditions the order asks for, across every LAJ row from the placement to its last derivation — **19 consecutive rows**:

| condition | result |
|---|---|
| **postable** (`53 < live_ask`) | **TRUE on all 19** — asks 54, 55, 56 |
| **pair budget** (`53 + 41 = 94 ≤ 99`) | **TRUE on all 19** — sibling SVA committed at 41 |
| **the leg's own floor admits it** | **FALSE on all 19** — `evidenced_floor` is **54** on every row |

So 53 was postable and affordable, and on every instant it was **below LAJ's observed traded low**. Under this build's own law a floor is a true trade; resting a cent under the observed low is a forecast that a new low will print. It eventually did — **at 1784052830.356, 1,857 s after LAJ had already filled at 54, and 2,013 s after LAJ's last derivation (1784050817)**.

**Attribution: DATA-GAP.** The evidence that 53 would print existed in no store at any instant the machine was awake. Taking it would have meant abandoning the definition the whole build was written to enforce.

### The other two games

**URSPAL meets spec at Δ3** (58 + 39 = 97) — and could have been Δ4: URS held 57, its exact corrected floor, from ln1326 ts 1784028269 and lost it to the singleton cancel at ln1364 (§3). **DANPRA has no under-par offer at any price** — DAN 59 + PRA 41 = 100 against par 99. PRA filled at 41; DAN rests at 58, the shallowest level its ATP_MAIN library can express against a floor of 59 that sits above its anchor. Unchanged DATA-GAP.

---

## 3 — The residual violation: lawful guard, unlawful fallback

`SINGLETON_SURVIVOR_ENVELOPE_NOT_CONSUMED` is now **one row**: 8 singleton rows, 7 consumed, 1 unconsumed.

| ln | ts | env | ask | lawful high | singleton | consumed | active before | action |
|---|---:|---|---:|---:|---:|---|---:|---|
| 1326 | 1784028269 | [57,58] | 58 | 57 | — | — | NONE | **PLACE 57** |
| **1364** | **1784030027** | **[58,58]** | 58 | 57 | 58 | **false** | **57** | **CANCEL** (`FAIL_LOUD_NO_LAWFUL_ATOMIC_REPLACEMENT`, `ENVELOPE_POINT_AT_OR_ABOVE_LIVE_ASK`) |
| 1365 | 1784031046 | [58,58] | **59** | 58 | 58 | **true** | NONE | PLACE 58 |

**Adjudication: the refusal is LAWFUL.** With the singleton at 58 and the ask at 58, `58 ≥ ask` — the level crosses and cannot be posted as a maker bid. It is not a refusal to act on a single-level conviction; it is the book declining the conviction's price. F-VS-156's ruling stands, and the row now names the reason honestly (`ENVELOPE_POINT_AT_OR_ABOVE_LIVE_ASK`).

**The defect is what happens next.** URS was standing at **57 — postable (57 < 58), lawful, and its exact corrected floor** — and the fallback cancelled it rather than holding it. It re-places 58 when the ask moves to 59 and fills at 58 on the 57 print. **Cost: 1¢. URSPAL settles 97/Δ3 where holding 57 gives 96/Δ4.** Unchanged from F-VS-156 and F-VS-160(c): the lawful behaviour is to hold the postable rest when the newly-narrowed belief is un-postable, not to abandon it.

---

## 4 — Capture-blind tenure (F-VS-173): REPAIRED

Three at-floor tenure episodes, 34 rows total:

| leg | level | rows | start | end | duration | qualifying prints ≤ level after the start | outcome |
|---|---:|---:|---:|---:|---:|---|---|
| URS | 58 | 6 | 1784031096 | 1784031347 | 251 s | yes — 57 @1784032697.601 | **filled** |
| LAJ | 54 | 18 | 1784036629 | 1784050817 | 14,188 s | yes — many, incl. 1784050973.063 | **filled** |
| PRA | 41 | 10 | 1784359766 | 1784369249 | 9,483 s | yes — incl. 1784369249.288 | **filled** |

**Every episode begins before a qualifying print, and every one ends in a fill.** At 453296b7 two of four began *after* the last qualifying print — BAR by 9,523.7 s scoring 22,975 s at a dead floor, GIU by 4,568.8 s. Both of those legs now have **no tenure episode at all, because they filled instead.** The metric is no longer scoring rests that could never trade. **F-VS-173 is closed.**

---

## 5 — LAJ rearm pending: the premise is a receipt artefact

`ATOMIC_REARM_RECEIPT.json` reports `pending_at_edge_legs: 1`, and for `KXATPCHALLENGERMATCH-26JUL14LAJSVA|LAJ`: `attempts 1497`, **`resolved: null`**, **`final_status: "REARM_PENDING"`**.

**The trace says it resolved.** LAJ's full rearm lifecycle:

```
ln3436  ts 1784020205        CANCEL_REST      status REARM_PENDING                  attempts 1
ln3437  ts 1784020209        HOLD_REST        status REARM_PENDING                  attempts 4
ln3438  ts 1784020209.484    HOLD_REST        status REARM_PENDING                  attempts 5
ln3439  ts 1784028911        HOLD_REST        status REARM_PENDING                  attempts 946
ln3440  ts 1784036624.369    PLACE_REST 54    status REARM_RESOLVED_WITH_LAWFUL_REST attempts 1499
                                              resolved_at_epoch 1784036624.369
```

The pending lasted **16,419.369 s** and closed with the rest that went on to fill at 54. LAJ's last derivation (ln3458, ts 1784050817) reads `NO_REARM_PENDING_OR_TRIGGERED`, and so does every other leg's.

**Why the receipt disagrees:** its per-leg reducer stops at `attempts: 1497`, which is the **last `REARM_ATTEMPT` row** (ln4961, ts 1784036611). The resolution is recorded on a **`DECISION_STAGE`** row 13.369 s later carrying `attempts: 1499`. The receipt consumes one row class and the resolution lives in the other.

**What it blocks: nothing.** There is no unresolved rearm at the edge in this run. All five cancels arm (`atomic_rearm.status` = `REARM_PENDING` on every one — I checked each), and all five resolve (`REARM_RESOLVED_WITH_LAWFUL_REST` on PAL, URS, LAJ, PRA, DAN). `EVERY_CANCEL_REARMS` passes honestly. The finding here is the receipt, not the machine: **`pending_at_edge_legs: 1` is false, and it is the third instance of a committed receipt disagreeing with the trace it summarises** (F-VS-170, F-VS-178).

---

## Verdict

CERTIFIED: three completions with seven fills, every one verified by trade_id against the raw print store and F-VS-107-clean; **BAR and GIU capture for the first time**, BAR by standing at 27 at the microsecond its floor printed; 23 orders with one per decision instant, reproduced over all orders — F-VS-176 closed; the DISAGREES lane no longer prices at the live bid, 0 of 3 against 214 of 214 — F-VS-165/177(a) closed; 131 literals with zero named survivors — F-VS-177(a) closed; 61/61 receipt producers with the F-VS-178 orphan given a real writer; the floor check now tests all 2,769 rows including the 279 null-floor rows — F-VS-177(b) closed; at-floor tenure episodes all begin before a qualifying print and all end in fills — F-VS-173 closed; determinism byte-identical ×2.

FAULTED: (i) `can_fail` is still `producer_store !== check_store` — the `counterexample_condition` strings are prose no predicate reads, so `gate_fields_that_can_fail: 14` is still a label count (F-VS-172 stands); (ii) `ATOMIC_REARM_RECEIPT.json` reports LAJ permanently pending when the trace shows it resolved, because its reducer reads only `REARM_ATTEMPT` rows — a third receipt-vs-trace contradiction; (iii) the singleton fallback still cancels a postable, floor-exact 57 instead of holding it, costing URSPAL a cent; (iv) the literal audit's "operational" classifier is a regex over line shape, so the 131 survivors are explained by pattern rather than derivation; (v) `DETERMINISM_RECEIPT.label` is stale from the prior build.

NOT FAULTS: neither remaining cent was available. GIU's 66 was at the ask at the only instant the machine was awake; LAJ's 53 was below its own observed traded low at every instant it could have been placed, and printed 1,857 s after LAJ had already filled.

---

# ADDENDUM — 12-lane counter-grade returned; my tenure verdict corrected

Filed as F-VS-184 … F-VS-185. Every figure re-measured by me before filing.

## A — Tenure is partially closed, not closed. The blindness flipped sign.

I wrote that at-floor tenure was repaired and that BAR and GIU have no episodes "because they filled instead." Half of that is right.

**The false-positive half is genuinely closed.** All three recorded episodes — URS 58, LAJ 54, PRA 41 — begin before a qualifying print and all three end in fills. No episode now scores a rest that could never trade. That was F-VS-173's complaint and it is answered.

**But GIU stood at its exact evidenced floor and scored zero.**

| leg | last order | fill | standing at that level | tenure rows | DECISION rows in the window |
|---|---|---|---:|---:|---:|
| BAR | 27 @1783841801.304 | 1783841801.417152 | 0.113 s | 0 | 0 |
| **GIU** | **67 @1783867786** | 1783869375.227061 | **1,589.227 s** | **0** | **0** |
| URS | 58 @1784031046 | 1784032697.600949 | 1,651.601 s | 6 | 6 |
| **PAL** | **39 @1784023248** | 1784042066.596112 | **18,818.596 s** | **0** | **1,125** |
| SVA | 41 @1784020209 | 1784020209.484174 | 0.484 s | 0 | 0 |
| LAJ | 54 @1784036624.369 | 1784050973.062825 | 14,348.694 s | 18 | 18 |
| PRA | 41 @1784359388 | 1784369249.287716 | 9,861.288 s | 10 | 10 |

GIU held its floor for **1,589.227 s** and the metric recorded nothing, because the trace contains **zero GIU `DECISION_STAGE` rows in (1783867786, 1783869375.227]**. Tenure is sampled at evaluation instants and GIU had none. **That is the same capture-blindness F-VS-173 named, surviving as a false negative instead of a false positive.** My "because they filled" explanation is true for BAR (0.113 s) and SVA (0.484 s) and false for GIU.

**And it misses the run's best-executed leg.** PAL stood at **39 — the governing W1TT-C-002 floor, captured exactly — for 18,818.596 s across 1,125 evaluation instants** and scored zero, because 39 is one cent *below* its running low of 40, so `active === evidencedFloor` is false. DAN likewise held 58 against a running low of 59 for 25,805 s, scoring zero. The metric rewards standing **at** the floor and is silent on standing **below** it, which is strictly better for a buyer and is what PAL did.

**The recorded durations understate the true standing intervals**, because `start_epoch` is the first receipt at which `active` is *already* at the floor — one evaluation instant after the order that created the rest:

| leg | reported | true standing | under-reported by |
|---|---:|---:|---:|
| URS @58 | 251 s | **1,651.601 s** | 1,400.601 s (84.8 %) |
| LAJ @54 | 14,188 s | 14,348.694 s | 160.694 s |
| PRA @41 | 9,483 s | 9,861.288 s | 378.288 s |

## B — SVA passed its own floor print

At **ln3435, ts 1784020201.83** — the exact instant of SVA's governing floor print (41 @1784020201.830010, trade `95992e7f`, size 27) — the build **repriced SVA to 40**, one cent under the arriving print, while its own `evidenced_floor` on that very row already read **41** (bid 40, ask 41, coherent lane). The floor print passed unfilled. SVA reached 41 at ln3437 ts 1784020209 and took the **second** 41 print at 1784020209.484174 — same price, **7.654 s late**.

Not a lost cent, but a lost 7.654 s of exposure at a level the machine had already named, and the one row in this build where a leg moved *away* from a floor its own evidence had established in the same object. It is why my §1 called SVA's capture clean: the price is right and the capture is real, but the first qualifying print was declined.

Separately, **the fill attribution is arbitrary and undisclosed**: two true prints share the microsecond 1784020209.484174 — `d97f0682` (size 6) and `62c5acca` (size 10) — and the `FILL_EVENT` names `62c5acca` with no stated rule for choosing between same-price, same-microsecond prints. Immaterial to price, material to reproducibility.

## C — What the lanes confirmed

The seven fills, the 23 orders with an empty multi-order set, the 0-of-3 live-bid result, the 131 literals with zero named survivors, 61/61 producers, the 2,769/2,769 floor coverage, and both cent adjudications all reproduce independently. One framing the lanes sharpen usefully: **the credited pair sums are worse than the tape's trigger prints on two games** — GIUBAR credited 94 against a trigger-print sum of 27+66 = 93, URSPAL credited 97 against 57+39 = 96 — because `STANDING_REST_LIMIT_CENTS` credits the maker at its own rest, which errs against the book. That is F-VS-107 working as written, and it is the whole of GIUBAR's missing cent.
