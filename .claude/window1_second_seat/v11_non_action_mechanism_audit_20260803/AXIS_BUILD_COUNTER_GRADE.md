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
