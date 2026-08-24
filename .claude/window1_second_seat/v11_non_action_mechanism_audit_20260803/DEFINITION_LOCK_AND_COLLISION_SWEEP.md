# DEFINITION LOCK + COLLISION SWEEP — OS @3c56730a

License: LAW_INDEX read this turn @ a2a6a25d, sha256 `41784e6ab62d6341…` — verified against the order's `41784e6a…`. Laws: L8 L11 L18 L20 L22 · welds.
Seat: CC verification. Every count measured by me from the custodied trace (66,527 lines / 3,198 leg-derivations), the raw print store, and the code at 3c56730a. Governing floors: W1TT-C-001 GIUBAR, W1TT-C-002 URSPAL; LAJSVA and DANPRA from the base table c0056976. `PAR_BUDGET_CENTS = 99` (`window1_v54_functionable_os.js:8`).

---

## 1 — THE DEFINITION LOCK (operator ruling, filed as law)

> Every load-bearing term — **floor · touch · low · entry · envelope · window · coherence** — has ONE vault definition. Any value carrying that name asserts its source at write time. **Two values for one term is a defect class.**

The lock has three obligations, and the OS already satisfies all three for exactly one term, which is the model to copy:

| obligation | the term that already meets it |
|---|---|
| one definition | **window** — `window_end_epoch` is a single number per game |
| source asserted at write time | **window** — every row carries `window_source: "L11_VERIFIED_REPLAY_WINDOW:<method>"` |
| the assertion is true | **window** — the four methods (`BOOK_SIGNATURE_OPERATOR_RULED`, `TAPE_SIGNATURE_OPERATOR_RULED`, `MACHINE_RECEIPT`, `TAPE_INFERENCE`) match the truth table's `bell_source` per game |

Everything below is measured against that standard.

---

## 2 — COLLISION SWEEP, ranked by decision consumption

Ranking rule: a value that **set a target** outranks one that **gated a boolean**, which outranks one that only **appears in a receipt**.

### RANK 1 — "LOW" means both a traded low and a book low, and it set targets

`own_evidence.basis` takes two values. Census over 3,198 derivations:

| basis | rows | `true_trade_count` |
|---|---:|---|
| `TRUE_TRADE` | 2,915 | 1–14 |
| **`BOOK_PATH`** | **283** | **0 on all 283** |

A `BOOK_PATH` low is a **quote** low — the leg's lowest displayed bid — with **zero trades behind it**. It occupies the same field as a traded low and carries the same name.

**It set targets.** `own_evidence.observed_low_cents` is read as `causalSeenLow` at `os.js:571` and becomes the rest through `upperQuantileRaw = causalSeenLow + q75` → `clamp` → `targets[legId]` (`os.js:572-601`). It is also read at `os.js:287-291` to make `predicted_cents`, which becomes `envelope.low_cents` via `supportedFloorLevel(criterion, predicted_cents)` at `os.js:470`.

**28 of the run's 60 PLACE/REPRICE actions were taken on a `BOOK_PATH` row**, and **3 were priced directly off one**:

| ln | leg | ts | action | `observed_low` | trades | q75 | → chosen | envelope | declared axis |
|---|---|---:|---|---:|---:|---:|---:|---|---|
| 235 | PAL | 1784016214 | REPRICE → 36 | 37 | **0** | +1 | 38 | [35,38] | `POST_FORMATION_TRUE_TRADE_LOW_CENTS` |
| 57275 | SVA | 1784016081.367 | REPRICE → 38 | 38 | **0** | 0 | 38 | [36,39] | `POST_FORMATION_TRUE_TRADE_LOW_CENTS` |
| **66486** | **DAN** | **1784332553** | **PLACE → 52** | **49** | **0** | 0 | **52** | **[52,58]** | `POST_FORMATION_TRUE_TRADE_LOW_CENTS` |

The third row is **DAN's 52** — the number the seat spent an entire order tracing in F-VS-145. Its origin is a book low of 49 with zero true trades, at `window_fraction: 0`, on the first receipt of the game, snapped onto a library level and stamped with the traded-low axis.

**The source assertion is present and false.** The envelope carries `target_axis: POST_FORMATION_TRUE_TRADE_LOW_CENTS` on all three rows. `own_evidence.basis` does assert `BOOK_PATH` truthfully one object away — but nothing downstream reads it, and the envelope's own axis field contradicts it.

The remaining 25 of the 28 are `OWN_EVIDENCE_AT_DISAGREES_SURVIVOR_SUPPORTED` rows, where the target is the live bid rather than the book low — a different collision (Rank 3) on the same rows. Among them: **ln37 BAR PLACE 29, ln46 BAR REPRICE 26, ln47 BAR REPRICE 25** (the three that cost GIUBAR its fill), **ln215 URS PLACE 57 / PAL PLACE 33**, **ln57260 LAJ 54 / SVA 36**.

### RANK 2 — "FLOOR" means both an envelope low and an observed traded low, and it gates every supervisor decision

Already filed as F-VS-159; the exact line is now settled:

```js
:851  const floorEvidenceCandidates = [
:852    { source: "CURRENT_SURVIVOR_ENVELOPE_LOW",       value: cent(decisionEnvelopes[legId]?.low_cents) },
:853    { source: "RUNNING_TRUE_TRADED_LOW",             value: cent(criterion?.observed_traded_low_cents) },
:854    { source: "PRIOR_CARRIED_SURVIVOR_ENVELOPE_LOW", value: cent(priorEnvelopes[legId]?.low_cents) },
:855  ].filter(…)
:856  const activeFloorEvidence = floorEvidenceCandidates.find((c) => c.value === active) ?? null;
:857  const evidencedFloor = activeFloorEvidence?.value ?? floorEvidenceCandidates[0]?.value ?? null;
```

`?? floorEvidenceCandidates[0]` selects **the envelope low by array position** whenever the standing rest is not sitting on a candidate. Measured: `evidenced_floor_source` is `CURRENT_SURVIVOR_ENVELOPE_LOW` on **2,604** rows, `PRIOR_CARRIED_…` on 152, `RUNNING_TRUE_TRADED_LOW` on **103**, none on 339. On the 2,563 rows carrying both an evidenced floor and an `observed_traded_low_cents`, the evidenced floor sits **below the traded low in the same object on 2,271 (88.6 %)** and equal on 292 — never above.

**It gates every supervisor decision** (`:950-951 proposalAtOrBelowFloor` / `proposalAdmitted`, all 3,198 rows) **and it sets targets** through the pre-allocation protection at `:749/:754`, which writes `targets[legId] = active`.

**The source is asserted at write time** (`evidenced_floor_source`) — and the assertion is honest. The defect is not the label; it is that two different measurements are allowed to answer to one name and the array order picks the belief.

### RANK 3 — "TOUCH" means both a live quote and an executed print

| field | value | rows |
|---|---|---:|
| `derivation.target_authority` | `EVIDENCED_TOUCH` | **3,198 / 3,198** |
| `derivation.evidence_rung` | `EVIDENCED_TOUCH` | **3,198 / 3,198** |
| `derivation.touch_relation` | `AT_EVIDENCED_TOUCH` | 3,185 |
| | `MAP_LICENSED_{1,2,3}C_BELOW_TOUCH` | 12 |
| | `CROSSED_BOOK_NOT_A_TOUCH` | **1** |

`target_authority` is constant across every row in the run — **including the 2,598 coherent rows where the target came from the Q75 quantile and no touch was consulted at all.** A field that cannot vary is a label, not an authority, and here the label is false on 81 % of rows.

Meanwhile the OS's own touch lane defines touch as the **live bid**:
```js
:735  targets[legId] = liveBid && liveAsk && liveBid < liveAsk ? liveBid : active;
:737  mode: "CONSUME_OWN_EVIDENCED_LIVE_TOUCH_WHILE_ENVELOPE_NULL"
```
while `LIVE_TOUCH_CONSUMPTION_RECEIPT.floor_touch_rows` / `floor_stood_rows` use touch to mean a rest meeting a **traded floor**. A bid is a quote; a floor touch is a trade. Two meanings, one word.

**Decision consumption:** the touch lane holds 243 rows - 242 holds and **1 action** — DAN `CANCEL_REST` at ln66507, ts 1784342553.971, on a **crossed book (bid 60 / ask 59)**. That row is the single `CROSSED_BOOK_NOT_A_TOUCH` in the run, so the OS *does* know a crossed book is not a touch — and its `target_authority` still reads `EVIDENCED_TOUCH`.

**The gate literal that denies this is false.** `REPAIR_GATE_RECEIPT.json` carries `live_bid_is_reference_only: true` — a typed-in literal (`build.js`). Measured: **all 50 PLACE/REPRICE actions in `OWN_EVIDENCE_AT_DISAGREES_SURVIVOR_SUPPORTED` have `target_cents == live_bid_cents`** — 50 of the run's 60 orders, 83 %. Across both live-bid lanes, `chosen_target_cents == live_bid_cents` on 391 of 431 rows. The live bid is not a reference; it is the price.

### RANK 4 — "WINDOW": one definition, one disagreement, and the source is asserted

| game | `window_end_epoch` | governed `span_end` | agree? | `window_source` |
|---|---:|---:|---|---|
| GIUBAR | 1783874300 | 1783874300 | ✓ | `BOOK_SIGNATURE_OPERATOR_RULED` |
| URSPAL | 1784042247 | 1784042247 | ✓ | `TAPE_SIGNATURE_OPERATOR_RULED` |
| LAJSVA | 1784078400 | 1784078400 | ✓ | `MACHINE_RECEIPT` |
| **DANPRA** | **1784373060** | **1784372160** | **✗ — 900 s long** | **`TAPE_INFERENCE`** |

`window_end_epoch` and `derivation.window_timing.window_end_epoch` agree on all 3,198 rows, and every row asserts its source. The one game that disagrees is the one whose window is inferred rather than ruled. DANPRA's window runs 900 s past its span end — the interval in which DAN's post-floor own-evidence rows sit.

### RANK 5 — "ENVELOPE": no collision

`layered_dual_belief.envelope` equals `conviction_evolution.effective_envelope` on **3,198 / 3,198**. `prior_envelope` differs from effective on 215 rows (that is movement, not disagreement) and `proposed_envelope` differs on **1** (ln1357, the run's single carried-conviction row). The envelope family has one authoritative reading and it is consistent.

### RANK 6 — "COHERENCE": one value and a hole, not two values

`coherence.status` and `coherence_placement.current_coherence` agree on **3,198 / 3,198**. The second reading, `envelope_placement.coherence_exists_at_receipt`, is **null on 339 rows** (26 COHERENT · 70 DISAGREES · 243 INSUFFICIENT_EVIDENCE) because the branches that would write it do not run. Not a collision — a field that asserts nothing on 10.6 % of rows.

### RANK 7 — "ENTRY": clean

`entry_cents` == `prior_standing_target_cents` on all four fills, each verified by `trade_id` against `fit-local/prints.jsonl`: URS `a4575e0c…` 58/58 (print 57), PAL `11b32855…` 39/39, LAJ `16abd619…` 54/54, PRA `54075ae0…` 41/41 — all `true_print: true`. `execution_price_basis` is `STANDING_REST_LIMIT_CENTS` throughout. No predicted, modelled or offered "entry" exists anywhere in the OS. F-VS-107 holds, and the term has one meaning.

---

## 3 — SELF-AGREEING CHECKS

The class that hid F-VS-159 through five audits. Three sub-classes, all measured.

### Class A — typed-in literals: 17 in the gate object alone, two of them false

`REPAIR_GATE_RECEIPT.json` fields whose value is a literal in `build.js`, not a measurement:

`telemetry_only` · `ask_reachability_defines_target` · **`same_receipt_write_then_read_removed`** · `hardcoded_stale_prior_false_gate_removed` · `floor_rest_locks_retired` · `unstamped_incomplete_scores_zero` · **`live_bid_is_reference_only`** · `may_hold` · `may_abstain` · `may_complete_only_from_own_live_evidenced_touch` · `placement_rule_changed_from_outcomes` · `named_event_ids_in_policy_source` · `rule_applied_uniformly` · `f_vs_110_tuned_stamp_retained` · `full_804_run` · `sealed_read` · `live_mutation`.

Two are **demonstrably false**:
- **`same_receipt_write_then_read_removed: true`** — F-VS-162. `prior_receipt_genuinely_readable` falls from 2,503/2,761 at 680e995c to **439/2,816** here, across 1,063 distinct receipts.
- **`live_bid_is_reference_only: true`** — 50 of 60 orders have `target == live_bid`.

`hardcoded_stale_prior_false_gate_removed: true` is itself a hardcoded literal asserting that a hardcoded gate was removed. `floor_rest_locks_retired: true` appears as a literal **four times** across the receipts; it happens to be true, and I verified it independently, but nothing in the build checks it.

**Independent source for this class:** a literal is not a check. Each must either be deleted or replaced by a predicate over the trace.

### Class B — the check reads the output of the thing it checks

| check | file:line | agrees with | measured |
|---|---|---|---|
| `every_blocked_or_refused_floor_proposal_has_real_reason` | `build.js:1417` | `supervisor_complete` (`os.js:972`), true on all 3,198 by construction | true |
| `urs_repriced_off_57` | `build.js:1401` | population at `:1380` filtered by `active_was_at_evidenced_floor`, which goes false at the moment the rest is abandoned | false — **and wrong** (F-VS-161) |
| `protected_from_conflicting_belief_or_cancel` | `os.js:945` | the mode string it is derived from, read as an outcome | true on 96 rows, two of which are cancels (F-VS-155) |
| `activeInconsistent` | `os.js:828` | `envelopeAuthoritativeAtReceipt` whitelist, which the placement mode determines | forced false on 2,589 of 2,624 envelope rows (F-VS-149) |
| `violations` *(retired)* | old `os.js:821` | the guard's own output, identical predicate | was 0 (F-VS-145) |

**Independent source:** the print store for anything about capture; the truth table for anything about floors; a second organ's record for anything about a decision. The rule the register needs: **a check must read a different store than the producer.**

### Class C — vacuous by construction

| check | file:line | why it cannot fail | measured |
|---|---|---|---|
| `no_not_required_stamp` | `build.js:1418` | forbids the substring `NOT_REQUIRED`, which the supervisor's status and reason enums (`os.js:957-968`) cannot produce | true |
| `every_prior_receipt_action_restates_basis_and_survivors` | `build.js:1353` | `.every()` over `carriedActionRows`, length 0 | vacuously true |
| `CARRIED_CONVICTION_ACTION_WITHOUT_LIVE_SUPPORT_OR_BASIS_RESTATEMENT` | `build.js:1946` | `.some()` over the same empty array | never fires |
| `every_reallocation_shows_from_not_equal_to` | `build.js:1445` | filters on `allocation.mode === "GRADED-CONTINUOUS-SPLIT"`; `allocation.mode` is **null on all 3,198 rows** | vacuously true |
| `every_split_preserves_pair_budget` | `build.js:1443` | reads `pair_conservation.at_or_below_99`, which `functionable_os.js:767` defines as `!(target && sibling) \|\| sum <= 99` — true whenever either side is null, and enforced by the allocator upstream | true; **2,464 of 3,198 rows have `sum_cents: null`** and passed without arithmetic |
| `every_sentence_states_required_depth_inputs` | `build.js:1431` | checks the sentence contains `WINDOW_SIDE_READ=`, `PRICE_AT_EVIDENCED_TOUCH=`, `MAP_CELL=`, `MAP_P50_CENTS=`, `MAP_MEMBERS=`, `CHOSEN_DEPTH_CENTS=`, `OWN_WINDOW=`, `PAIR_STATE=` — each occurs **exactly once** in `functionable_os.js`, as literal template text | true |
| `every_sentence_names_basis` · `every_sentence_states_allocation` · `every_target_states_touch_relation` | `build.js:1432/1442/1454` | same — `EVIDENCE_RUNG=`, `ALLOCATION=`, `TOUCH_RELATION=` are template literals | true |
| `stale_envelope_originated_new_rest` | `os.js:888` | hardcoded `false` in every row; nothing reads it | false on 3,198 |

**Independent source:** for the sentence checks, compare the sentence's *values* against the row's fields, not its keys against its own template. For the pair-budget check, evaluate the arithmetic on the rows where both legs carry a target — 734 of 3,198 — and report that denominator.

---

## Verdict

**One term meets the lock: `window`.** One number per game, source asserted on every row, assertion true — with a single measured disagreement (DANPRA, 900 s, `TAPE_INFERENCE`).

**Two terms are clean but unlabelled: `entry` and `envelope`.** Both have one meaning; neither asserts its source at write time. They pass today by discipline, not by construction.

**Three terms carry two values: `low`, `floor`, `touch`** — and all three are decision-consuming. `low` set three targets directly, including DAN's 52. `floor` gates every one of the 3,198 supervisor decisions and sets targets through the protection branch. `touch` labels 3,198 rows with an authority that is false on 2,598 of them, and the gate literal denying it — `live_bid_is_reference_only: true` — is contradicted by 50 of the run's 60 orders.

**`coherence` has a hole rather than a collision**: 339 rows where the second reading is null.

**And the checking apparatus cannot see any of it.** 17 gate fields are typed-in literals, two of them false. Five checks read the output of the thing they check. Eight more cannot fail by construction. The remedy the Definition Lock implies is mechanical: **every value carrying a locked term must be written with a `_source` sibling naming the store it came from, and every check must read a different store than the producer.** On today's evidence that would have caught F-VS-159 at write time, and `live_bid_is_reference_only` on the first order.

---

# ADDENDUM — 12-lane sweep returned; two of my claims corrected, three terms added to the lock

Filed as F-VS-168 … F-VS-170. Every row below re-derived by me from the primary source before filing.

## A — Corrections

**(a) "LOW" is a silent SUBSTITUTE, not two live values. The class was wrong; the defect is not.**

Measured over all 3,198 derivations, comparing `own_evidence.observed_low_cents` against `criterion.observed_traded_low_cents` **in the same row**:

| basis | relation | rows |
|---|---|---:|
| `TRUE_TRADE` | traded low **equals** the own-evidence low | **2,759** |
| `TRUE_TRADE` | traded low null | 156 |
| `BOOK_PATH` | traded low **null** | **283** |
| any | the two present and **different** | **0** |

The two lows never coexist with different values. `functionable_os.js:498-499` reads
```js
const ownLow   = ownEvidence.true_trade_low_cents ?? ownEvidence.book_path_low_cents;
const ownBasis = Number.isFinite(ownEvidence.true_trade_low_cents) ? "TRUE_TRADE"
               : Number.isFinite(ownEvidence.book_path_low_cents)  ? "BOOK_PATH" : "NO_OWN_LOW";
```
— a **fallback**, not a competitor. So the correct statement of the defect: *one term, one definition, **two producers**, and the substitution is invisible to every downstream consumer*, which then reads the number under `target_axis: POST_FORMATION_TRUE_TRADE_LOW_CENTS`. Under the Definition Lock that is still a violation — the value's source assertion is false — but it belongs to a **substitution** class, not a collision class, and the lock needs both.

Everything measured in F-VS-164 stands: 283 `BOOK_PATH` rows all with `true_trade_count: 0`, 28 of 60 orders taken on one, and the three directly-priced rows including DAN's PLACE 52.

**(b) The envelope chain runs on 46 of the 283, not all of them.** `predicted_cents` is set on all 283; `envelope.low_cents` on **46**. The other 237 carry no envelope at all, because `proposedEnvelopes` is built only under `coherentNow` (`os.js:467`). The 28 actions and the 3 direct-priced rows are unaffected.

**(c) F-VS-167's `activeInconsistent` entry carried a 680e995c figure onto 3c56730a.** I wrote "forced false on 2,589 of 2,624 envelope rows"; that was the measurement from the previous build (F-VS-149), where the retired lock pinned rests far below their envelopes. **At 3c56730a only 25 rows in the whole run have a standing rest outside its envelope**; `active_inconsistent_before_action` is **true on 22**, and the `envelopeAuthoritativeAtReceipt` whitelist (`os.js:824-827`) suppresses it on exactly **3**:

| ln | leg | ts | rest | envelope | mode |
|---|---|---:|---:|---|---|
| 234 | PAL | 1784016213 | 34 | [35,38] | `EVIDENCED_FLOOR_REST_HELD_CURRENT_SURVIVOR_SUPPORT` |
| **1397** | **URS** | **1784030027** | **57** | **[58,58]** | `EVIDENCED_FLOOR_REST_HELD_CURRENT_SURVIVOR_SUPPORT` |
| 66504 | DAN | 1784339306.774 | 52 | [57,59] | `EVIDENCED_FLOOR_REST_HELD_CURRENT_SURVIVOR_SUPPORT` |

The mechanism is unchanged and it is small — but **ln1397 is the row where the belief dropped 57** (F-VS-160(c)), and ln66504 is DAN's own floor instant. The suppression fires three times and twice on a row that mattered.

## B — Three terms added to the lock

**"LOW", third producer — the book MID.** `functionable_os.js:177-182`:
```js
function referenceOf(row) {
  if (row.kind === "PRINT" && cent(row.price_cents))        return row.price_cents;
  if (row.kind === "BOOK"  && cent(row.last_trade_cents))   return row.last_trade_cents;
  if (row.kind === "BOOK"  && cent(row.bid_cents) && cent(row.ask_cents))
                                                            return Math.floor((row.bid_cents + row.ask_cents) / 2);
  return null; }
```
`:210 running_low_cents = Math.min(running_low_cents, reference)` — so `book_path_low_cents` (`:627`) is a running minimum over a series whose third branch is a **mid-quote**, i.e. a number that never traded and is not even a bid. That is the value the fallback at `:499` promotes into `own_evidence.observed_low_cents` on 283 rows.

**"LOWER BOUND" — a load-bearing floor with no name in the record.** `lowerBounds[legId]` is set in six places (`os.js:599, 648, 661, 701, 736, 756`) and consumed at `os.js:378`:
```js
const headroom = Object.fromEntries(ids.map((id) => [id, Math.max(0, out[id] - lowerBounds[id])]));
```
inside `allocateUnderPar`. It decides which leg absorbs a par excess. **It is never emitted to any receipt under any name** — 10 references in the OS, all internal. It is the number that made SVA absorb the whole 1¢ at ln57287 (F-VS-160(b)): LAJ's headroom was `59 − 59 = 0` because `lowerBounds.LAJ` was its envelope low. A term that decides a cent and appears in no record cannot be audited at all.

**"COMPLETED" and "DELTA_VS_100_CENTS" — two values, one receipt.** `REPAIR_GATE_RECEIPT.json` carries both at once:

| object | LAJSVA | source |
|---|---|---|
| `honest_baseline_pins` | `completed: true, delta_vs_100_cents: 6` | `build.js:1994` → `row.lineage_receipt` (a **prior run**) |
| `layered_safety_floor_breaks` | `completed: false, delta_vs_100_cents: null` | `build.js:1233` → `row.layered_dual_belief` (**this run**) |

Neither object says which run it describes. A reader taking `completed` from the gate gets `true` or `false` depending on which array they open. This is the collision class the lock names, on a term not in the operator's list of seven — and it is the term the whole bed is graded on.
