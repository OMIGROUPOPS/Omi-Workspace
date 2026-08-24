# AXIS BUILD COUNTER-GRADE — @680e995c

License: LAW_INDEX @ 680e995c, sha256 41784e6a… · L8 L11 L18 L20 L22 · F-VS-134/135 · TWO-WAY STREET F-VS-122 · welds.
Seat: CC verification. Every number measured by me from the custodied trace (6039baa5de77…, 94,254,970 B), the package receipts and the code at 680e995c. Corrected floors/spans per W1TT-C-001/002.

## Headline

**The traded-low axis is real. The floor protection built on it is directional, and its sign is backwards for capture.** It arms on whatever rest a leg places *first* — below the floor on 6 of 8 legs — then forbids moving **up** toward the floor, while leaving a move **down off** the floor unguarded. URSPAL stood at its exact floor 57 for 6.4 hours and was repriced down to 52 by the new DISAGREES lane; that is the regression.

## 1 — Verification

| claim | verdict |
|---|---|
| custody | 4 artifacts externally custodied (trace, FLOOR_REST_PROTECTION 105,479,214 B, ENVELOPE_PLACEMENT, CARRIED_CONVICTION) — all present on disk, bytes and sha256 match. Lawful under L22; `FLOOR_REST_PROTECTION_RECEIPT.json` is absent from the commit **by design**, not missing |
| floor-rest protection, 2,759 rows | **COUNT CONFIRMED** from the trace: mode `FLOOR_REST_PROTECTED_SUPPORTING_ELIMINATIONS_NOT_OVERTURNED` on exactly 2,759 derivations (URS 1,146 · PAL 1,175 · BAR 164 · GIU 145 · SVA 62 · LAJ 44 · DAN 22 · PRA 1) |
| "violations: 0" | **TRUE BUT CIRCULAR.** The violation predicate is `priorFloorLockBinding && (!Number.isInteger(target) \|\| target > active)` (`dual_belief_os.js:821`) — it counts only cancels and **upward** moves. A downward vacate off a locked floor is not expressible as a violation. See §2 |
| `urs_57_to_58_recurrence: false` | **TRUE and misleading** — the upward 57→58 I filed in F-VS-142(a) did not recur; URS lost the same floor rest downward instead |
| 49 / 11 / 0 DISAGREES licensing | **RECONCILED AND CONFIRMED**: 49 derivations carry mode `OWN_EVIDENCE_AT_DISAGREES_SURVIVOR_SUPPORTED`; of those 11 act (6 PLACE + 5 REPRICE) and 38 HOLD; 0 unlicensed placements. **All 49/49 have `own_evidence_target_cents == live_bid_cents`** — the lane places at the live bid |
| traded-low axis live | **CONFIRMED, in the matcher not just labels**: `TRADED_LOW_SHAPE_SUPPORT_BINDING.json` axis `POST_FORMATION_TRUE_TRADE_LOW_CENTS`, `ask_reachability_role: INFORMS_EXECUTABILITY_ONLY_NEVER_DEFINES_FLOOR_OR_SHAPE_MATCH`, 39 shapes / 39 with support / 844 member bindings; runtime rows carry `candidate_final_floor_levels_cents`. This answers F-VS-143's target-vs-criterion finding |
| carry branch | still **0** (`prior_receipt_placements_or_reprices: 0`) |
| fills | 2 only: LAJ 54 @1784036624.369 and PRA 41 @1784342553.971 |

## 2 — The floor lock: what it is, and why it blocks

It is a **derived** value, not a hardcoded constant — there is no literal 52 anywhere in the policy (`dual_belief_os.js` integer literals are only 0, 1, 20, 100). It is `state.dual_belief.floor_rest_locks[legId]`, armed at a leg's **first placement** and carrying `target_cents`, `supporting_shape_ids`, `eliminated_shape_ids_at_lock`, `armed_at_epoch` (`:545-550`).

Protection fires only when the proposal would vacate **upward or cancel**:
```
:713  const beliefWouldVacateFloorUpward = floorLockSupported && (!Number.isInteger(targets[legId]) || targets[legId] > active);
:717  if (floorLockSupported && beliefWouldVacateFloorUpward) { targets[legId] = active; … may_cancel_or_reprice_upward: false }
```

What each leg actually locked, against its corrected floor:

| leg | lock target | armed | floor | lock vs floor | first block |
|---|---:|---|---:|---|---|
| URSPAL URS | **57** | 1784001495 | 57 | **at the floor** | blocked 58 |
| DANPRA DAN | **52** | 1784332553 | 59 | 7¢ below | blocked 57 |
| GIUBAR GIU | 63 | 1783831858 | 66 | 3¢ below | blocked 64 |
| GIUBAR BAR | 25 | 1783841774 | 27 | 2¢ below | blocked 26 |
| LAJSVA LAJ | 54 | 1784007603 | 51 | 3¢ above | blocked 55 |
| LAJSVA SVA | 36 | 1784007603 | 41 | 5¢ below | blocked 37 |
| URSPAL PAL | 33 | 1784001495 | 39 | 6¢ below | blocked 34 |
| DANPRA PRA | 41 | 1784332553 | 41 | **at the floor** | — |

**The 52 the order names is DAN's lock**, armed at its first placement (a Q75-inside-envelope number, envelope `{low 52, high 58}`, anchor 58), 7¢ under its floor 59. On **6 of 8 legs the lock arms below the floor and the upward block then forbids convergence to it** — DAN 52→57 refused, GIU 63→64 refused, BAR 25→26 refused, PAL 33→34 refused. The protection is not protecting a floor; it is freezing a first guess and preventing the walk to the floor.

It is also the carry-branch blocker in the direct sense: with the lock pinning `targets[legId] = active` on 2,759 of 3,143 rows, the placement path never reaches a state where a prior-receipt conviction could originate anything — the carry branch stays 0.

## 3 — The last cent, and 0/8 narrowing

Admissible traded-low levels (`candidate_final_floor_levels_cents`) at each leg's floor moment, with its rest:

| leg | floor | rest | anchor | survivors | admissible levels (n) | floor in set? |
|---|---:|---:|---:|---:|---|---|
| GIUBAR BAR | 27 | 25 | 31 | 4 | 9 — 17,19,20,22,23,24,25,26,**27** | YES |
| GIUBAR GIU | 66 | 63 | 67 | 3 | 12 — …62,63,64,65,**66**,67 | YES |
| URSPAL PAL | 39 | 31 | 38 | 4 | 14 — 24…37,38,**39** | YES |
| URSPAL URS | 57 | 52 | 62 | 3 | 8 — 41,47,48,52,53,54,**57**,58 | YES |
| LAJSVA SVA | 41 | 36 | 41 | 2 | 9 — 27,29,30,36,37,38,39,40,**41** | YES |
| DANPRA PRA | 41 | 41 | 41 | 3 | 6 — 35,37,38,39,40,**41** | YES |
| LAJSVA LAJ | 51 | 54 | 59 | 1 | 11 — 38,44,49,**50**,54,55,…,60 | **NO** (stops 1¢ short at 50) |
| DANPRA DAN | 59 | 52 | 58 | 3 | 8 — 22,52,53,54,55,56,57,**58** | **NO** (stops 1¢ short at 58) |

**The order's premise needs correcting on both halves.** For LAJ and DAN the exact floor is *not* supported — the member-backed set stops precisely **1¢ short** (50 vs 51; 58 vs 59). That is the real "last cent": a coverage edge in the traded-low bins, not a placement choice. Conversely, on the **six** legs where the floor *is* in the admissible set, the machine still did not rest there.

So the order's fork resolves as **both, with the second decisive**: no leg narrows to a single level (6–14 admissible levels, mean ≈9.6, so 0/8 confirmed), **and** placement does not consume the narrowing — the target is set by the Q75/own-evidence expression and the lock, never by choosing a member-backed level. On six legs the bins contained the answer and the placement path never looked at them.

## 4 — The URSPAL regression, attributed

URSPAL completed 99/Δ1 at b229d5dc. Here it completes nothing (PAL 31 / URS 52, no fills). Decisive step, from rows:

- **URS PLACE_REST 57 @1784001495** — at formation, via `OWN_EVIDENCE_AT_DISAGREES_SURVIVOR_SUPPORTED`, live bid 57. **That is its exact corrected floor.** The floor lock armed on it, and protection then refused 58 on 1,146 rows.
- **URS REPRICE_REST 57 → 52 @1784024516** — same lane, `live_bid_cents: 52`, `own_evidence_target_cents: 52`, `running_true_trade_low_cents: 64`, coherence DISAGREES, envelope null. The bid had fallen; the lane followed it down. Protection did not fire because `targets > active` is false for a downward move.
- URS's floor printed at **1784032697.601 — 8,182 s later**. A 52 bid does not fill on a 57 print. The rest had stood at the floor for 23,021 s (6.4 h) and was given up before the floor arrived.
- PAL followed the same lane down 33 → 32 → 31.

**Attribution: MISREAD.** Nothing was missing and nothing went unconsulted — the machine had the floor level standing, licensed and survivor-supported, and its own touch-following rule moved it off. The named step is the DISAGREES-own-evidence lane setting `own_evidence_target_cents = live_bid_cents` (49/49) with no floor-lock guard on the downward direction (`:713`).

**Did the axis change cause it?** No — the axis realignment is sound and is what put URS at 57 in the first place. The regression comes from the two repairs built *on top* of it: a touch-following DISAGREES lane and a one-directional lock.

## Verdict

CERTIFIED: the traded-low axis is genuinely live in the matcher; the 2,759 protected rows and the 49/11/0 licensing reconcile exactly; custody is lawful and complete; determinism and stories pending lane confirmation.
FAULTED: (i) floor protection arms on the first rest, not on a supported floor, and blocks upward convergence on 6 of 8 legs; (ii) its violation metric is upward/cancel-only, so "violations: 0" cannot see the failure that occurred; (iii) the new DISAGREES lane is the touch lane renamed — 49/49 rests at the live bid — and it walked URS off its own floor, costing the only completion; (iv) placement still ignores the member-backed level sets it now computes, on six legs that contained the floor.

---

# ADDENDUM — 12-lane counter-grade returned; four of my own claims corrected, and the cost measured

Filed as F-VS-148 … F-VS-152. Every number below re-derived by me from the custodied trace, both builds' traces, the raw print store `C:/Users/omigr/OMI-Window1-private/fit-local/prints.jsonl`, the corrections file at 15955e44, and the code at 680e995c. Where a lane and I disagreed I went to the primary source; two lane claims are rejected below.

## A — Corrections to my own F-VS-144 … F-VS-147

**(a) "Custody lawful and complete" was over-stated.** `SURVIVOR_SHAPE_LIBRARY_BINDING.json` names two libraries as causal inputs with sha256 — `INTERIM_PAIR_LIBRARY_V18.json` (`4542b46d…9849e2`) and `PAIR_COUPLE_LIBRARY_V19.json` (`73469a96…5b947b`). **Both are absent from the 680e995c tree and absent from `EXTERNAL_CUSTODY_MANIFEST.json`** (whose five entries are FOUNDATION_PER_MINUTE_UNIVERSE plus the four receipts). Separately, that manifest records `PHASE_CENTRAL_ESTIMATE_SURFACE.json` at sha `f02eca7a…` with no `bytes`, while the committed blob is `52667e21…` / 8,497 B — which `ARTIFACT_HASH_MANIFEST.json` records correctly. Two manifests disagree on one committed file.

**(b) I omitted the build's own top-line verdict.** `REPAIR_GATE_RECEIPT.json`: `safety_floor_pass: false`, `self_stop: true`, `stop_reason: "BED_TRIPWIRE_BREAK_AFTER_TRADED_LOW_AXIS_FLOOR_PROTECTION_REPAIR"`, three `layered_safety_floor_breaks` (GIUBAR, URSPAL, LAJSVA) against `honest_baseline_pins` URSPAL Δ3 / LAJSVA Δ6. The build declares its own failure; my §1 table did not say so.

**(c) The lock table mixed vintages, and "6 of 8 below the floor" was wrong.** Every lock transition in the run: **BAR 29→26→25 · PAL 33→32→31 · URS 57→52**; GIU 63, LAJ 54, SVA 36, DAN 52, PRA 41 single. Zero upward transitions, zero nulls. So the **first** arm is below the floor on **4 of 8** (GIU 63/66, PAL 33/39, SVA 36/41, DAN 52/59), **at** it on 2 (URS 57, PRA 41), and **above** it on 2 — **BAR armed at 29 against a floor of 27**, and LAJ at 54 against 51. The **final** lock is below on 6 of 8. My table reported BAR's third lock (25) as if it were its first.

**(d) My carry-branch clause is refuted.** The carried-placement branch is `else if (decisionEnvelopes[legId])` at `:659` — reachable only when **not** `coherentNow`, because `:551 if (decisionEnvelopes[legId] && coherentNow)` takes precedence. The run's single carried-conviction row (ln 1341, URS @1784028256) is **COHERENT**, so the carried branch never executed; mode `CARRIED_PRIOR_RECEIPT_CONVICTION_Q75_BASIS_RESTATED` appears **0 times in 3,143 rows** and `carriedPlacement` (`:828`) is false by branch precedence, not by the floor lock. `prior_receipt_placements_or_reprices: 0` is a precedence result.

**(e) "The axis is what put URS at 57" is wrong.** At ln 215 (ts 1784001495, `…URSPAL-URS.csv.gz#row-9`) `running_true_trade_low_cents` **and** `traded_low_target_criterion.observed_traded_low_cents` are both **null**. The 57 is the **live bid**; the axis only permitted it by membership. The exoneration verdict survives on better evidence — see §D and §F.

**(f) SVA's floor epoch — my own error, not the build's.** The corrections file at 15955e44 holds exactly two records, **W1TT-C-001 = GIUBAR** and **W1TT-C-002 = URSPAL**; there is no LAJSVA correction. The base table at c0056976 gives `legB_SVA floor_c 41, floor_epoch 1784020201.8`, which is SVA's **first** 41 print (`prints.jsonl`, 1784020201.830010). The value I have been carrying, **1784020209.484**, is the second/third 41 print and the prior build's SVA fill instant. **There is no corrections-law violation on SVA** — I reject that lane claim. My §3 SVA level count (9) was read at the wrong moment; at the governed epoch the set is 11, `[27,29,30,36,37,38,39,40,41,42,44]`. Floor 41 is in the set either way.

## B — The veto is the mechanism, and the consistency check that should have caught it is switched off

**1,484 blocked proposals at the exact corrected floor** — PAL 1,113 @39 · BAR 151 @27 · GIU 132 @66 · SVA 46 @41 · URS 42 @57.

And the deeper number: **2,589 of 3,143 rows stand a rest strictly below their own effective envelope low** (PAL 1,142 · URS 1,142 · BAR 131 · GIU 131 · LAJ 21 · SVA 19 · DAN 3). **All 2,589 are stamped `active_inconsistent_before_action: false`, `resolution: "NOT_REQUIRED"`, `envelope_authoritative_at_receipt: false`.** `envelopeAuthoritativeAtReceipt` (`:786-789`) whitelists only `CONDITIONED_DISTRIBUTION…` and `CARRIED_PRIOR_RECEIPT_CONVICTION_Q75…`; the floor-lock overwrite makes the mode neither, so the inconsistency test can never fire. It is authoritative on **32 of 3,143 rows** — the DANPRA coherent placements. The lock disables its own supervisor.

Also dead by construction: **0 of 2,901 lock rows ever recorded a reinstatement**, and `eliminated_shape_ids_at_lock` is `[]` on **2,782 of 2,901** — a lock armed with an empty elimination basis has no overturn path. `FLOOR_REST_PROTECTED_SUPPORTING_ELIMINATIONS_NOT_OVERTURNED` reduces to an unconditional `FLOOR_REST_PROTECTED`.

## C — The belief *did* narrow to one level. Placement did not consume it.

| leg | effective envelope | rows | standing rest | corrected floor |
|---|---|---:|---:|---:|
| GIUBAR GIU | **[66, 66]** | 131 | 63 | 66 |
| GIUBAR BAR | [27, 32] | 131 | 25 | 27 |
| URSPAL PAL | low 39 | 1,107 | 33/32/31 | 39 |
| URSPAL URS | low 57 | 42 | 52 | 57 |

GIU's envelope collapses to **exactly its corrected floor, a single cent, and holds there for 131 consecutive rows** — ln 83 ts 1783873872 through ln 213 ts 1783874300, the corrected span end — with the rest 3¢ below it the whole way. BAR's envelope low is its exact floor on the same 131 rows.

So the order's fork resolves cleanly: `separated_to_one_exact_level_legs: 0` measures the **candidate level set**, and on that axis nothing narrows (6–14 levels). But the **belief envelope** narrowed to one level equal to the floor, and the placement path never reached it. **Not consuming the narrowing is decisive.**

## D — What it cost, from the raw print store

Counterfactual test: from the first receipt at which the machine proposed the level, does a true in-span print at or below it exist?

| leg | vetoed / abandoned level | verdict | settling print |
|---|---:|---|---|
| GIU | 66 (first block 1783867224) | **WOULD HAVE FILLED** | 66 @1783869375.227, again 1783871011.999, 1783872611.499 |
| PAL | 39 (first block 1784021161.637) | **WOULD HAVE FILLED** | 39 @1784042066.596 (the only ≤39 print, 20,905 s later) |
| URS | 57 (held from 1784001495) | **WOULD HAVE FILLED** | 57 @1784032697.601 (the only ≤57 print) |
| SVA | 41 (first block ts 1784020209) | **PROVEN — same receipt** | prior build repriced SVA 40→**41 at ts 1784020209** and filled at 1784020209.484 |
| BAR | 27 | veto worthless — **0 of 151** blocks precede the 27 print (earliest 1783851291, 9,489.7 s after it) | — |
| BAR | **29 (the original rest)** | **WOULD HAVE FILLED** — lost to the *downward* ratchet | 27 @1783841801.305; BAR repriced 29→26 @1783841772 and 26→25 @1783841774, **29.3 s and 27.3 s before it**. Min BAR print in span is 27, so 26 and 25 never fill |
| DAN | 59 | no capture available | own evidence named 59 exactly at 4 receipts (1784347255 / 1784348215 / 1784369249 / 1784370685, bid 59 **and** running_true_trade_low 59) and the ladder (max 58) refused each by 1¢ — but all three ≤59 prints (1784339306.775, 1784340781.176, 1784342267.087) precede them |

**SVA is a second same-receipt inversion.** Prior build: `ln7120 SVA REPRICE_REST → 41 ts 1784020209`, fill @1784020209.484. This build, same trace second: proposal 41, `FLOOR_REST_PROTECTED`, lock 36, refused. Same tick, opposite outcome — the URS 1784028269 pattern repeated on a second game.

**Pair arithmetic under the 99 par budget:**

- **URSPAL** 57 + 39 = **96** (Δ4) — completes
- **GIUBAR** 66 + 29 = **95** (Δ5) — completes
- **LAJSVA** 54 (actually filled) + 41 = **95** (Δ5) — completes
- **DANPRA** 59 + 41 = **100** (0¢ offered) — `LAWFUL_INCOMPLETE`, correctly stamped

**Three of the four games are inside the floor lock.**

## E — The lane that produced the lost fill is gone

| | b229d5dc | 680e995c |
|---|---:|---:|
| DECISION_STAGE | 1,599 | 1,595 |
| REARM_ATTEMPT | **8,353** | **0** |
| FILL_EVENT | 4 | 2 |
| CANCEL_REST | 7 | **0** |
| PLACE / REPRICE | 12 / 16 | 8 / 5 |

Fills — prior: URS 58 (`ATOMIC_REARM_LAWFUL_REPLACEMENT`), PAL 41, SVA 41, PRA 41. This build: LAJ 54, PRA 41. **URS, PAL and SVA are all lost; LAJ is gained; PRA moved 26,695 s earlier onto the exact print that set its floor.** F-VS-107 holds on all six fills across both builds — entry equals the standing rest every time.

The prior URS fill was licensed by the atomic-rearm lane, which emits nothing at all here (`ATOMIC_REARM_RECEIPT.json` `per_leg: []`). Attribution **DATA-UNCONSUMED**: the lane that generated the winning rest is silent, and F-VS-147 attributed the URSPAL loss to the DISAGREES reprice alone.

## F — Verdict, restated

CERTIFIED unchanged: traded-low axis genuinely live in the matcher; 2,759 protected rows and 49/11/0 licensing reconcile; determinism `V54_..._DETERMINISM_X2` all-byte-identical across 2 runs per game (replay stability, not cross-host); stories carry all four elements on 3,143/3,143 with 0 ACTION/TARGET mismatches; both fills verified by trade_id against `prints.jsonl` to sub-millisecond.

FAULTED, now measured: the floor lock arms on the first rest and never releases (0 reinstatements, empty elimination basis on 2,782 rows); it blocks 1,484 proposals at the exact corrected floor and disables the envelope-consistency check on 2,589 rows; the belief narrowed to a single cent equal to the floor on GIU and was ignored; **and on the print record GIUBAR, URSPAL and LAJSVA all complete under par without it.** The axis is not the cause — at ln 765 it is the only reason the ratchet stopped at URS 52 instead of 51 — and the build's own gate already says `safety_floor_pass: false`.
