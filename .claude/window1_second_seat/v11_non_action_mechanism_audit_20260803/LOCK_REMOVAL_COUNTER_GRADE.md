# LOCK-REMOVAL COUNTER-GRADE — @3c56730a

License: LAW_INDEX @ 3c56730a, sha256 41784e6a… · L8 L11 L18 L20 L22 · TWO-WAY STREET F-VS-122 · F-VS-134/135 · welds.
Seat: CC verification. Every number below measured by me from the custodied trace (99,605,078 B), the prior traces, the raw print store `fit-local/prints.jsonl`, the corrections file at 15955e44 and the code at 3c56730a. Governing floors: W1TT-C-001 GIUBAR, W1TT-C-002 URSPAL; LAJSVA and DANPRA from the base table c0056976 (SVA 41 @1784020201.8 — corrected per F-VS-148(f)).

## Headline

**The lock is genuinely gone and the build banked the two fills I said were available on the coherent lane. It lost the other two to mechanisms that were underneath the lock all along: a supervisor that admits every downward chase, and an atomic-replacement path that turns the one reprice that matters into a cancel plus a place two seconds later.** My F-VS-151 counterfactual was a claim about *price availability*. It holds — the build reached 4 of the 5 levels. What it did not model is **tenure**: only 2 were still standing when the print arrived.

---

## 1 — Verification

| claim | verdict |
|---|---|
| lock retirement | **CONFIRMED.** `floor_rest_locks`, `beliefWouldVacateFloorUpward`, `targetIsEvidencedFloor` all gone. The subtree is rebuilt around `evidenced_floor_cents` / `evidenced_floor_source` / `active_was_at_evidenced_floor` / `protected_from_conflicting_belief_or_cancel`. `floor_rest_locks_retired: true` on every row |
| `protected_rows: 96` | **CONFIRMED** — mode `EVIDENCED_FLOOR_REST_HELD_CURRENT_SURVIVOR_SUPPORT` on exactly 96 of 3,198 derivations (PAL 64 · BAR 11 · LAJ 11 · URS 5 · DAN 4 · PRA 1). Down from 2,759 |
| 1,563 / 1,576 admissions | **PARTIALLY REPRODUCED.** From the trace's own `proposal_supervisor` subtree I count **1,672 supervised** (`supervisor_required: true`), of which **1,658 ADMITTED** and **14 BLOCKED**, plus 1,526 `NO_AT_OR_BELOW_FLOOR_PROPOSAL` — total 3,198. The gate's 1,672 matches exactly. Its **1,576 / 1,563 is 96 / 95 lower** and I cannot reproduce that denominator from the trace; `NARROWING_AND_PROPOSAL_SUPERVISOR_RECEIPT.json` (183,197,694 B) defines its own set. Flagged, not settled |
| supervisor reasoning | **IT DOES NOT REASON.** `:951-952 proposalAdmitted = proposalAtOrBelowFloor && Number.isInteger(target) && target <= evidencedFloor`. Its whole test is "is the proposal at or below the evidenced floor". For admitted rows `reason` is literally `action.reason`; for blocked rows `` `${allocation.reason}:${action.reason}` ``. It restates decisions taken elsewhere. And `supervisor_complete = !proposalAtOrBelowFloor \|\| Boolean(action.reason && allocation.reason)` is **true on all 3,198 rows** — a metric that cannot be false, the same class as the retired `violations: 0` |
| rearm restoration | **RESTORED IN BEHAVIOUR, UNRECORDED IN ITS RECEIPT.** REARM_ATTEMPT 0 → **64,906** (PAL 27,918 · URS 27,918 · LAJ 4,535 · SVA 4,535; GIUBAR and DANPRA **zero**), across 4,233 distinct timestamps with a peak of **558 attempts at one timestamp** (1784024910). Every attempt carries `rearm: null`. Meanwhile `ATOMIC_REARM_RECEIPT.json` is `per_leg: []`, `resolved_legs: 0`, `pending_at_edge_legs: 0` and the gate reads `atomic_rearm.legs: 0` — **while both URSPAL fills carry `standing_license_basis: "ATOMIC_REARM_LAWFUL_REPLACEMENT"`.** The lane licensed the completion and its own receipt records nothing |
| custody | **MY F-VS-148(a) IS ANSWERED.** `INTERIM_PAIR_LIBRARY_V18.json` and `PAIR_COUPLE_LIBRARY_V19.json` are now in `EXTERNAL_CUSTODY_MANIFEST.json`; I verified both blobs at 189eaa20 in the local object store and their sha256 match the binding (`4542b46d…`, `73469a96…`). The custody_location is a raw.githubusercontent URL — online-only in form, but the same commit resolves offline via git, so lawful in substance. Five local custody files present, **bytes exact on all five**. **Unreconciled:** the manifest lists 8 entries and declares `oversized_artifacts_moved_to_external_custody: 5` |
| determinism | `V54_REMOVE_FLOOR_LOCK_CONSUME_NARROWING_DETERMINISM_X2`, `runs_per_game: 2`, `all_byte_identical: true`. Replay stability on one tape and one host — not cross-machine, not cross-seed |
| URSPAL fills | **BOTH VERIFIED BY trade_id IN `prints.jsonl`.** URS `a4575e0c…` print 57 @1784032697.600949; PAL `11b32855…` print 39 @1784042066.596112. Both `true_print: true`. F-VS-107 holds on all four fills — URS 58/58, PAL 39/39, LAJ 54/54, PRA 41/41 |
| gate's own verdict | `safety_floor_pass: false`, `self_stop: true`, `stop_reason: BED_TRIPWIRE_BREAK_AFTER_FLOOR_LOCK_RETIREMENT_AND_NARROWING_CONSUMPTION`, `zero_measured_law_violations: false`, three named `law_violations`. The build reports its own failure |

---

## 2 — The counterfactual gap: reaching is not holding

My F-VS-151 claim, tested leg by leg against this build:

| leg | my claim | what happened | gap |
|---|---|---|---|
| **PAL 39** | would have filled | **VINDICATED.** PLACE 39 @1784023248 (coherent lane, env [39,43]); held 18,818.6 s; filled at the single ≤39 print, 1784042066.596. Exact corrected floor captured | none |
| **URS 57** | would have filled | **PARTIALLY.** PLACE 57 @1784028256.439 — its exact floor — then **CANCELLED at 1784030288** on the singleton rule (§3.2); re-placed 58 @1784031046; filled at 58 on the 57 print | **1¢** |
| **GIU 66** | would have filled | **NOT REALISED.** Rested 66 from 1783867224, then REPRICE **66→65 @1783867786** on the DISAGREES lane at live bid 65 — **1,589.2 s before** the first 66 print. All three 66 prints (1783869375.227 / 1783871011.999 / 1783872611.499) land while GIU rests at 65. It returns to 66 at 1783873872, **1,261.2 s after the last one** | whole fill |
| **SVA 41** | proven at the identical receipt | **NOT REALISED, by 2.516 s.** Reached 41 at **1784020212**; the last 41 print was **1784020209.484174** | whole fill |
| **BAR 29** | would have filled | **NOT REALISED — unchanged from the prior build.** REPRICE **29→26 @1783841772** on the DISAGREES lane at live bid 26, **29.305 s before** the 27 print. BAR reaches 27 at 1783851291, 9,489.7 s after it, and no ≤27 print follows | whole fill |

**What else blocks them — three named steps, all rows:**

**(i) The supervisor admits the chase.** GIUBAR ln82, GIU @1783867786: proposal 65, `evidenced_floor_cents` 67, status **`ADMITTED_AT_OR_BELOW_EVIDENCED_FLOOR`**. The move that gave up 66 was *admitted* — because `proposal <= evidencedFloor` is the entire test. Downward is always admitted. The supervisor has no notion of a rest already standing where the tape is about to go.

**(ii) On the rows that cost BAR, there is no evidenced floor at all.** GIUBAR ln46, BAR @1783841772: `evidenced_floor_cents: null`, status `NO_AT_OR_BELOW_FLOOR_PROPOSAL`, envelope null, coherence DISAGREES. The whole new organ is **inert** on the exact row that cost the fill. The DISAGREES bid-follower (`OWN_EVIDENCE_AT_DISAGREES_SURVIVOR_SUPPORTED`, target = live bid) is unsupervised.

**(iii) The atomic-replacement path converts a reprice into a cancel.** LAJSVA ln57287, SVA **@1784020209** — the receipt at which the prior build repriced 40→41 and filled 0.484 s later — proposal 41, `evidenced_floor_cents` **38**, so `41 > 38` → status `NO_AT_OR_BELOW_FLOOR_PROPOSAL` → **HOLD_REST 40**. One second later, ln57288 @1784020210: `evidenced_floor_cents` now 41, proposal 41, status **`BLOCKED_OR_REFUSED_WITH_REASON`**, reason `ATOMIC_REPLACEMENT_UNAVAILABLE_FAIL_LOUD_INCONSISTENT_ONLY` → **CANCEL_REST**, both pair targets nulled. PLACE 41 lands at ln57289 @1784020212. **The 41→41 move needed two receipts and the print was in between.**

The same block hit PAL 11 consecutive times (ln255–ln265, 1784022240 → 1784023248, proposal 39, floor 39, final target null) — PAL survived only because its print was 18,818 s away.

**Attribution under F-VS-122.** BAR: **MISREAD** — the leg's own rest at 29 was fillable, the bid-follower overwrote it with no floor evidence in the row. GIU: **MISREAD** — the supervisor read a downward chase as an admissible floor proposal. SVA: **MISREAD** — the evidenced floor lagged the leg's own book by one receipt (38 while the bid was 41), and the atomic path spent the second that remained. No DATA-GAP in any of the three: every number needed was in the row.

**Discriminator.** Both floor-exact captures (PAL 39, PRA 41) and the one 1¢-short capture (URS 58) were priced by `CONDITIONED_DISTRIBUTION_FLOOR_SIDE_INSIDE_COHERENT_ENVELOPE`, ahead of the tape by 18,818.6 s, 10,001.0 s and 1,651.6 s. All three misses were last moved by `OWN_EVIDENCE_AT_DISAGREES_SURVIVOR_SUPPORTED`, which sets the rest to the current live bid and therefore arrives at a level only once the market is already there.

---

## 3 — The three self-reported failures, rows

### 3.1 `EVIDENCED_FLOOR_REST_REPRICED_OR_CANCELLED_WITHOUT_OVERTURN` — 2 rows, both cancels

| ln | leg | ts | evidenced floor | source | active before | proposal | action |
|---|---|---:|---:|---|---:|---:|---|
| 265 | URS | 1784023248 | 63 | `CURRENT_SURVIVOR_ENVELOPE_LOW` | 63 | 63 | **CANCEL_REST** |
| 57288 | LAJ | 1784020210 | 59 | `PRIOR_CARRIED_SURVIVOR_ENVELOPE_LOW` | 59 | 56 | **CANCEL_REST** |

Both carry `active_was_at_evidenced_floor: true`, `supporting_shapes_still_alive` non-empty, `supporting_eliminations_overturned` absent — nothing was overturned. Both also carry **`protected_from_conflicting_belief_or_cancel: true` AND `violation: true` on the same row**: the organ reports the rest as protected while the cancel executes. That flag is defined at `:945` as `mode === "EVIDENCED_FLOOR_REST_HELD_CURRENT_SURVIVOR_SUPPORT"` and is being read as an outcome when it is only a mode label.

**But the law is mis-specified, not the behaviour.** In both rows the "evidenced floor" is a **survivor-envelope low — the machine's belief — not a traded floor.** URS's corrected floor is 57, not 63; LAJ's is 51, not 59. Cancelling a bid resting 6¢ and 8¢ above the tape is correct conduct; at 63+39 = 102 and 59+41 = 100 neither rest could have completed under par. The law as written forbids abandoning any belief-priced rest, and it inherits the exact category error that armed the retired lock: *envelope low counted as an evidenced floor.*

### 3.2 `SINGLETON_SURVIVOR_ENVELOPE_NOT_CONSUMED` — the `rest < ask` condition is lawful; its fallback is not

The condition, `window1_v54_dual_belief_os.js:87-93`:

```js
function chooseEnvelopePlacementTarget(envelope, quantileTarget, lawfulEnvelopeHigh) {
  const singleton = envelope?.low_cents === envelope?.high_cents ? envelope.low_cents : null;
  if (Number.isInteger(singleton) && Number.isInteger(lawfulEnvelopeHigh) && singleton <= lawfulEnvelopeHigh) {
    return { target_cents: singleton, singleton_level_cents: singleton, singleton_consumed: true };
  }
  return { target_cents: cent(quantileTarget), singleton_level_cents: singleton, singleton_consumed: false };
}
```
with `:576 lawfulEnvelopeHigh = Math.min(envelope.high_cents, liveAsk - 1)`. For a singleton, `high === singleton`, so the binding term is **`singleton <= liveAsk - 1`** — i.e. `rest < ask`.

**Is it lawful? Yes.** It is the post-only guard. A resting bid at or above the ask crosses and executes as a taker; the whole seat premise — F-VS-107, maker fills price at the rest — requires `bid < ask`. It is **not** of the retired lock's class: the lock suppressed a belief on no market basis, whereas this refuses a level the book genuinely will not accept as a maker bid at that instant.

**The defect is the fallback.** All 7 unconsumed rows are one episode, URS 1784030288–1784030535, singleton **58**, ask **58**, `lawfulEnvelopeHigh` **57**:

| ln | ts | env | ask | lawfulHigh | singleton | consumed | active before | action |
|---|---:|---|---:|---:|---:|---|---:|---|
| 1358 | 1784028256.439 | [57,58] | 58 | 57 | — | — | NONE | PLACE_REST **57** |
| **1398** | **1784030288** | **[58,58]** | 58 | 57 | 58 | **false** | **57** | **CANCEL_REST** (`FAIL_LOUD_NO_LAWFUL_ATOMIC_REPLACEMENT`) |
| 1399–1404 | …–1784030535 | [58,58] | 58 | 57 | 58 | false | NONE | restless, 6 rows |
| 1405 | 1784031046 | [58,58] | **59** | **58** | 58 | **true** | NONE | PLACE_REST **58** |

**URS was standing at 57 — its exact corrected floor — and the singleton rule cancelled it.** The belief narrowed to [58,58]; the ask forbade 58; the fallback returned a null quantile target; the standing 57 was dropped rather than kept. 758 s restless, then 58, then the fill at 58 on the 57 print.

**Cost: 1¢ on the only completion.** URSPAL settles 58+39 = **97** (Δ3) where holding 57 gives 57+39 = **96** (Δ4). The singleton consumption organ was built to answer my F-VS-150 — the belief *did* narrow and placement did not consume it — and the first thing it did with that power was give up a rest already at the floor because the newly-narrowed belief named a cent the market would not take.

### 3.3 `FAIL_LOUD_CANCEL_WITHOUT_REARM_STATE`

22 cancels in the run. REARM_ATTEMPT rows exist for URSPAL (55,836) and LAJSVA (9,070) and **zero for GIUBAR and DANPRA**. GIUBAR has no cancels, so its zero is lawful. **DANPRA has one: DAN `CANCEL_REST` @1784342553.971 (`CONSUME_OWN_EVIDENCED_LIVE_TOUCH_WHILE_ENVELOPE_NULL`, bid 60 / ask 59 — a crossed book) and it produced no rearm state at all.** DAN then sat restless 4,721 s and re-placed 58 at 1784347275. That is the row. Compounding it: `ATOMIC_REARM_RECEIPT.json` asserts `no_permanent_silence: true` with `per_leg: []` — it cannot see the silence because it records nothing.

---

## 4 — Carry is still 0 of 3,198. The current blocker, with rows.

**It is structurally unreachable, and the lock was never the cause.** (This confirms my F-VS-148(d) self-correction from the other direction: the lock is gone and carry did not move.)

The placement chain at 3c56730a:

```
:566   if (decisionEnvelopes[legId] && coherentNow)        -> CONDITIONED_DISTRIBUTION_FLOOR_SIDE_INSIDE_COHERENT_ENVELOPE
:651   } else if (coherence.status === "DISAGREES")        -> OWN_EVIDENCE_AT_DISAGREES… / DISAGREES_HOLD…
:682   } else if (decisionEnvelopes[legId])                -> CARRIED_PRIOR_RECEIPT_CONVICTION_Q75_BASIS_RESTATED  (:703)
```

The carried branch requires **an envelope AND not coherent AND not DISAGREES**. Census over all 3,198 derivations:

| coherence | has envelope | rows |
|---|---|---:|
| COHERENT | yes | 2,624 |
| DISAGREES | no | 331 |
| INSUFFICIENT_EVIDENCE | no | 243 |

**Every row with an envelope is COHERENT, and every non-COHERENT row has no envelope. The guard is satisfied on 0 of 3,198 rows.** Mode `CARRIED_PRIOR_RECEIPT_CONVICTION_Q75_BASIS_RESTATED` therefore appears **0 times**, and `carriedPlacement` at `:867` — which tests exactly that mode string — is false by construction. `prior_receipt_placements_or_reprices: 0` is **a counter that cannot increment**, not a measurement of behaviour.

The recording side is live and disjoint from it: `:508 else if (coherence.status !== "DISAGREES" && prior && priorConviction && eliminationsStillHold && basisRestated && priorReceiptReadable)` fires once — **ln1357, URS @1784028256, coherence COHERENT**, `basis_re_stated true`, `eliminations_still_hold true`, `prior_receipt_genuinely_readable true`, prior envelope [63,64] — and the row's placement mode is `CONDITIONED_DISTRIBUTION_FLOOR_SIDE_INSIDE_COHERENT_ENVELOPE` with `carried_conviction_consumed_for_action: false`. **Carry can be recorded only at COHERENT rows and consumed only at non-COHERENT ones.** The two conditions are mutually exclusive.

The gate's `zero_action_blocker` lists six `conviction_evolution.update` strings; that is a census of what was observed, not a diagnosis. The blocker is one line: `:682` is an `else if` on a state that never co-occurs with a carried envelope. Removing the same-receipt write-then-read and the hardcoded stale-prior gate (both confirmed in the diff) changed nothing, because neither was the guard.

---

---

## 5 — The root of §2 and §3.1: the evidenced-floor selector prefers the envelope low over the traded low in the same object

Everything above converges on one line. `evidenced_floor_source` census over all 3,198 derivations:

| source | rows |
|---|---:|
| `CURRENT_SURVIVOR_ENVELOPE_LOW` | 2,604 |
| `PRIOR_CARRIED_SURVIVOR_ENVELOPE_LOW` | 152 |
| `RUNNING_TRUE_TRADED_LOW` | 103 |
| none | 339 |

On the 2,563 rows where both an `evidenced_floor_cents` and a `target_criterion.observed_traded_low_cents` exist in the same object:

| relation | rows |
|---|---:|
| evidenced floor **below** the observed traded low | **2,271 (88.6 %)** |
| equal | 292 |
| above | 0 |

The envelope low is the **deepest admissible level**, not the observed floor. The organ reads the traded low into the row and then names a number under it as "the evidenced floor."

**SVA, at its own floor instant.** ln57285, ts **1784020201.83** — the exact epoch of SVA's first 41 print:

```
env [38, 41]   target_criterion.observed_traded_low_cents = 41   anchor_cents = 41
evidenced_floor_cents = 38   evidenced_floor_source = CURRENT_SURVIVOR_ENVELOPE_LOW
action = HOLD_REST 40
```

Same at ln57286 and at **ln57287 @1784020209**, the receipt where the prior build repriced to 41 and filled 0.484 s later. Only at ln57288 — after the envelope goes null and the source switches to `RUNNING_TRUE_TRADED_LOW` — does `evidenced_floor_cents` become 41, half a second past the last 41 print.

**This is why the supervisor was blind.** Its admission test is `proposal <= evidencedFloor`. With the evidenced floor systematically *below* the true traded low, a proposal **at** the traded low scores `41 > 38` and is classified `NO_AT_OR_BELOW_FLOOR_PROPOSAL` — 1,526 rows — and passes with no supervision at all. The supervisor is structurally blind to exactly the proposals it exists to protect.

**Third appearance of one category error.** F-VS-145: the retired lock armed on `currentEnvelope.low_cents` and called it an evidenced floor. F-VS-155: the new violation law forbids abandoning a rest at an "evidenced floor" that is an envelope low. Here: the supervisor's floor input is the same number. The lock was removed; the error underneath it was not.

---

## Verdict

CERTIFIED: the floor lock is retired in substance, not renamed — 2,759 protected rows → 96, and the belief now reaches the floor on 4 of the 5 levels I named. PAL captured its exact corrected floor on the single print that set it; URSPAL completed at 97; determinism is byte-identical X2; all four fills verify against the raw print store by trade_id and satisfy F-VS-107; the V18/V19 custody gap I filed at 680e995c is closed.

FAULTED: (i) the proposal supervisor adjudicates nothing — its admission test is `proposal ≤ evidenced floor`, so it admitted the reprice that cost GIU its fill, and `supervisor_complete` is true on all 3,198 rows by construction; (ii) on the DISAGREES rows where two of the three misses happened there is no evidenced floor at all, so the organ is inert exactly where the losses occur; (iii) the atomic-replacement path spends a receipt on every reprice and that receipt is what SVA lost the fill by — 2.516 s; (iv) the singleton `rest < ask` guard is lawful but its fallback cancelled a standing rest at URS's exact floor and cost 1¢ on the only completion; (v) both self-reported floor-rest violations are cancels of belief-priced rests mislabelled as floors — the law inherits the retired lock's category error; (vi) DAN's cancel produced no rearm state and the rearm receipt that would show it is empty while 64,906 attempts sit in the trace; (vii) carry is structurally unreachable and its counter cannot increment; (viii) underneath all of it, the evidenced-floor selector names the envelope low as the floor on 2,271 of 2,563 rows where the traded low sits in the same object — the third appearance of the error that armed the retired lock.
