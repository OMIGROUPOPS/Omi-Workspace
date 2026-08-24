# CONTINUITY BUILD COUNTER-GRADE — @b229d5dc

License: LAW_INDEX @ b229d5dc, sha256 41784e6a… · L8 L11 L18 L20 L22 · F-VS-134/135 · TWO-WAY STREET F-VS-122 · welds.
Seat: CC verification. Every number below re-measured by me from the custodied trace (fc4aba4aa4…, 84,686,823 B), the package receipts, `fit-local/prints.jsonl`, and the code at b229d5dc.

## Headline

**The ruling is implemented faithfully — and it changed nothing.** b229d5dc is behaviourally IDENTICAL to f5fb8e8f on the bed: 2,366 distinct coherent placement keys `(event, leg, timestamp)`, present in both builds, **zero differing targets**; identical outcomes; identical deadline table (2,636 rows / 1,509 graded / 603 hits). The survivor-shape restoration and the carried-conviction machinery are, so far, pure instrumentation.

## 1 — Verification

| claim | verdict |
|---|---|
| 22 carried-conviction placements | **RECOUNTED = 22, but MISLABELLED.** All 22 are PLACE/REPRICE rows where a prior conviction merely *existed at another receipt*; their update kinds are CONFIRMED 12 · SHIFTED 9 · TIGHTENED 1 — so `effective = proposed`, i.e. **the envelope used was the current receipt's fresh proposal**, re-stamped with the current `belief_receipt`. The genuine carry branch `CARRIED_PRIOR_RECEIPT_CONVICTION_WITH_CURRENT_BASIS_RESTATEMENT` (`dual_belief_os.js:460-462`, `effective = prior`) fired **0 times in 3,141 derivations**. Update census: CONFIRMED 2,589 · DISAGREES 279 · NO_LAWFUL_ENVELOPE 242 · SHIFTED 13 · TIGHTENED 10 · FORMED 8 · CARRIED **0** |
| same-receipt write-then-read removed | **CONFIRMED.** `L429-431` deep-copies `priorEnvelopes` *before* the write; `priorReceiptReadable` (L451) additionally requires `belief_receipt !== state.receipt`. A read at receipt N cannot return a value written at N |
| F-VS-134 obligations emitted | **CONFIRMED.** The sentence carries `SURVIVOR_SHAPES=…` and `CONVICTION_EVOLUTION=…` (L805), the latter containing the update kind, prior/proposed/effective envelopes, `supporting_shape_ids_before/still_alive`, `eliminations_still_hold`, and a `movement_statement` naming what was eliminated/reinstated |
| survivor trajectories | **CONFIRMED**: 8 legs, 95 trajectory rows, 13 eliminations, **0 reinstatements**, every leg seeded from its full category set. Statelessness is genuinely gone — survivors carry receipt-to-receipt and narrow monotonically |
| overturn test carried | **CONFIRMED** — `eliminationRecord` (`survivor_shape_elimination.js:197-203`) stores `overturn_test` and `last_rechecked_receipt` per elimination; `every_live_elimination_has_overturn_test: true`. This honours F-VS-135(d). It has never fired: 0 reinstatements |
| touch actions zero | **CONFIRMED** — `NO_ENVELOPE_TOUCH_LANE_CENSUS`: 521 no-lawful-envelope receipts, 242 touch-lane receipts, **`touch_lane_actions: 0`**, `carried_conviction_actions: 22` |
| fills by trade_id + F-VS-107 | **CONFIRMED 4/4** against prints.jsonl (price, ts ±10 ms, `true_print`): URS 57 @1784032697.601 `a4575e0c` · PAL 40 @1784041997.986 `34d9e70c` · SVA 41 @1784020209.484 `62c5acca` · PRA 41 @1784369249.288 `6a5b1a68`. **Entry == standing rest on all four** (URS 58, PAL 41, SVA 41, PRA 41 — PAL's 41 rest filled on a 40 print, correctly credited at the limit) |
| determinism | **CONFIRMED** — each game replayed twice, byte-identical before any score receipt |
| lawful-incomplete | DANPRA **LAWFUL_INCOMPLETE** with `rest_at_floor_proven: true`, 16 rows, proof `59+41=100; max(0,99-100)=0` — F-VS-121 now fully closed. GIUBAR UNSTAMPED (no rest ever stood at either floor), LAJSVA UNSTAMPED (1 row) |

### Queued item closed — f5fb8e8f
0-of-2,767 **reproduced exactly**: 2,620 `CONDITIONED_DISTRIBUTION_FLOOR_SIDE_INSIDE_COHERENT_ENVELOPE` + 147 `DISAGREES_HOLD_OR_REDERIVE_NO_PLACEMENT`, zero subordination rows. Its own gate self-stops honestly (`BED_TRIPWIRE_BREAK_AFTER_TOUCH_SUBORDINATION_AND_INSIDE_SPREAD_REACH`), rest-pricing clean (4 fills, entry == rest). **Disposition: CLEAN-BUT-INERT, and now superseded-without-behavioural-change by b229d5dc.** The wire was not defective — its guard (`beliefMode` and not coherent and not DISAGREES) simply never occurred, because every receipt on this bed is either coherent or DISAGREES.

## 2 — Miss forensics, two-way attributed

**(a) URSPAL Δ1** — lawful floors 39+57 = 96 (Δ4); paid 41+58 = 99 (Δ1). **PAL paid +2, URS +1.** Both rests were set inside a coherent envelope by the Q75 inside-spread reach; PAL's floor 39 printed at 1784042066.596, **69 s after** its 41 fill. → **DATA-UNCONSUMED** on both cents: the same conditioned population's lower quantiles reach 39 and 57, and the Q75 choice is the step that priced above them.

**(b) LAJSVA — what stopped LAJ.** SVA captured its floor 41 exactly. LAJ's lifecycle is short: PLACE 61 @1784016081.4 → REPRICE 59 @1784020201.8 → **CANCEL @1784020205** → nothing for the remaining ~11 h. At the cancel receipt: `COHERENCE=COHERENT`, live bid **56** / ask **58**, `lawful_envelope_high_cents: 57`, **`lawful_envelope_exists: false`** — the carried envelope's low (59) sat *above* `ask−1`, so no lawful target existed and the rest was cancelled. Crucially the conviction was `CONFIRMED_CARRIED_CONVICTION` at that very receipt with **`survivors_now: 1`** and `eliminations_still_hold: true`. LAJ's floor 51 printed at 1784060123.2 with no rest standing. → **MISREAD**: the conviction was "confirmed" against a survivor set of size one while the book fell 3¢ away from it; the named step is `eliminationsStillHold = supportIntersection.length > 0` (`dual_belief_os.js:448`), which passes on a single surviving shape and so cannot register the contradiction.

**(c) DANPRA** — PRA 41 is a floor capture at the audited floor price, entry == rest, trade-id verified. DAN: PLACE 49 → 57 → 58 → **59 @1784347255** → 58 → CANCEL @1784360967. DAN *reached its floor level 59* — but **7,948 s after** its floor printed (1784339306.8). Game is offer-0 (59+41 = 100), so the abstain is **LAWFUL-INCOMPLETE, not blocked**, and is now stamped with 16 proven rest-at-floor rows.

**(d) GIUBAR** — BAR: 213 stages, and its **only** rest is PLACE 32 @1783873872, 428 s before the bell and 8.9 h *after* its floor. At the 27 floor print (1783841801.304) the state was `COHERENCE=DISAGREES`, envelope **null**, live bid **25** / ask **30** — the 27 traded inside the spread, and the DISAGREES branch sets `may_originate_rest: false`. So nothing could stand. The Q75 inside-spread reach was live on 131 of BAR's stages but not on that one. GIU: **never placed a rest at all** in 213 stages. → **DATA-UNCONSUMED** for BAR (the live book and the print were both at the receipt; the coherence gate forbade use); GIU is a total non-participation.

## 3 — Survivor quality: eliminations fire on the wrong axis

Elimination matches shapes on `MACRO_KEYS = ["ask_net","ask_dip","ask_peak","ask_drawdown_from_peak"]` plus a `macroState` derived from the same ask path (`survivor_shape_elimination.js:15, 35-43, 49-56`) — an **ask-quote-path** axis. Capture depends on the **traded-low depth and its timing**. These are different axes, and for BAR the decisive event (a 27 print with the ask at 30) is *invisible* on the elimination axis by construction.

Survivor set at each leg's audited floor moment:

| leg | survivors / seeded | content |
|---|---|---|
| GIUBAR BAR | 1/4 | `PATH_UNUSABLE_REMAINDER` only |
| GIUBAR GIU | 1/3 | `PATH_UNUSABLE_REMAINDER` only |
| DANPRA DAN | 1/3 | `PATH_UNUSABLE_REMAINDER` only |
| DANPRA PRA | 1/3 | `PATH_UNUSABLE_REMAINDER` only |
| LAJSVA LAJ | 1/3 | `PATH_01_ORD_0_1` |
| LAJSVA SVA | 2/4 | `PATH_01_ORD_0_1`, `PATH_02_ORD_2` |
| URSPAL PAL | 4/4 | nothing eliminated |
| URSPAL URS | 3/3 | nothing eliminated |

**On 4 of 8 legs the sole survivor at the floor moment is the catch-all `PATH_UNUSABLE_REMAINDER`** — narrowing terminated on the bin that by name and construction predicts nothing. On 2 of 8 (both URSPAL legs) nothing was eliminated at all — vacuous. Only 2 of 8 (LAJ, SVA) carry a real, narrowed, usable set. And because `eliminations_still_hold` passes on one survivor, a conviction can be CONFIRMED indefinitely against the unusable remainder — which is exactly what happened to LAJ.

## Verdict

CERTIFIED: statefulness is real and monotone, overturn tests are carried, the same-receipt read is genuinely gone, the movement is stated in every sentence, touch actions are zero, all four fills are rest-priced and trade-id verified, determinism is byte-identical, and DANPRA's lawful-incomplete is now proven.
FAULTED: (i) "22 carried-conviction placements" mislabels 22 freshly-priced proposals — the carry branch is 0/3,141; (ii) `eliminationsStillHold` passes on a single survivor, which let LAJ confirm a conviction while the book left it and cost the 51 floor; (iii) elimination fires on the ask-quote axis while capture depends on the traded low, leaving 4/8 legs holding only the unusable remainder at their floor and 2/8 with no eliminations at all; (iv) the whole restoration produced **zero** behavioural change against f5fb8e8f. The ruling's intent is not yet tested.

## Addendum (F-VS-140) — the zero-change claim, strengthened to the full trace

The headline was filed on coherent placement rows only. It now rests on a direct derivation-by-derivation diff of both custodied traces:

| measure | f5fb8e8f | b229d5dc |
|---|---|---|
| derivation rows | 3,141 | 3,141 |
| COHERENT / DISAGREES / INSUFFICIENT_EVIDENCE | 2,620 / 279 / 242 | 2,620 / 279 / 242 |
| fills | SVA 41, PAL 41, URS 58, PRA 41 | identical, same timestamps |
| distinct (event, leg, ts, receipt) keys | 2,886 | 2,886 (0 unique to either) |
| differing (action, target, reason) | — | **0 of 2,886** |

This also closes the one soft spot in the filed evidence: f5fb8e8f's `ENVELOPE_PLACEMENT_RECEIPT` holds 147 `DISAGREES_HOLD_OR_REDERIVE_NO_PLACEMENT` rows and b229d5dc's holds none, which could have signalled a real difference. It does not — **both traces contain 279 DISAGREES derivations**; only the receipt routing changed. The restoration changed not one action, target or reason.

## Addendum 2 (F-VS-141..143) — self-correction after adversarial refutation

I ran a four-lane adversarial refutation against my own filed findings. It landed. Corrections, all re-verified by me at rows:

**F-VS-137 — amended, headline survives.** The evidence string "row-identical diff of both ENVELOPE_PLACEMENT_RECEIPTs" is inaccurate: 2,767 rows vs 2,620; identity holds on the coherent subset only. More importantly I missed a real change: `beliefMode` was **redefined** — `Boolean(state.dual_belief.current_envelopes)` (f5fb8e8f:432, true even for `{}`) → `openIds.some((id) => Boolean(decisionEnvelopes[id]))` (b229d5dc:503). That flips belief state true→false on 146 derivations (all DISAGREES stages), and propagates: 130 `allocation.reason` strings, ATOMIC_REARM attempts 8,406→8,401, COHERENCE_TIMELINES and `LAJ_FLOOR_MOMENT_BELIEF_INPUTS.envelope_at_stage` → null. **b229d5dc is not "pure instrumentation" — a guard's semantics changed; it changed no action.** The action-level identity and F-VS-140 stand. Also: calling all 22 "fresh proposals" is unfair to the 12 CONFIRMED rows, where the effective envelope equals the prior numerically and `migrated` is false — the accurate statement is `effective === proposed` on all 22.

**F-VS-138 — two attributions withdrawn.**
- **URSPAL (a)**: my "lower quantiles reach 39 and 57" is impossible — `clamp(upperQuantileRaw, envelope.low_cents, lawfulEnvelopeHigh)` (`:523-524`) makes `envelope.low_cents` a hard floor. The real finding is worse: **URS held a rest at its floor** (PLACE 57 @1784028269, envelope [57,58]) and its **own belief moved 57→58** @1784030007, cancelling the at-floor rest @1784030027 and re-placing at 58; the 57 print then filled 58. **MISREAD**, not DATA-UNCONSUMED.
- **LAJSVA (b)**: I misquoted L448 and, decisively, `eliminationsStillHold` sits only in `else if` branches after `if (proposed)` (L454) — unreachable at a coherent receipt, so causally inert where I blamed it. The package's own `LAJ_FLOOR_MOMENT_BELIEF_INPUTS.json` (which I did not use) shows the real cause at the floor moment: stage 1784059613, `envelope_at_stage: null`, **live bid 51 = the floor**, ask 53, DISAGREES, `may_originate_rest: false`. LAJ was lost to the **DISAGREES gate — the same mechanism as BAR**, so both take one class, not two.
- **(c)** stands, cause refined: DAN printed 59 three times with ask 59 and post-only cap 58 — structurally unrestable, not merely late. **(d)** GIU's non-participation is a description, not an attribution; it remains **open** under F-VS-122.

**F-VS-139 — rewritten.** Withdrawn: the "wrong axis" headline (the library's own target *is* `ask_reachable_low_cents`; the real gap is **target-vs-criterion** — ask-reachable low vs traded print floor); "predicts nothing" (the remainder is the deep tail of an ordered ladder, and is the correct label for GIU); and the closing clause blaming LAJ's loss on the remainder, which contradicts my own table — LAJ's sole survivor was `PATH_01_ORD_0_1`. Strengthened: `eliminations_still_hold` is a **tautology**, not a weak threshold — TRUE 3,141/3,141, survivor sets never empty, and the DROPPED branch is dead code 0/3,141.

**Where the refutation was itself wrong — corrections law upheld.** It claimed BAR's floor is 16 @1783875275.3 and PAL's 39 is out of span. Both read the uncorrected `c0056976` rows. W1TT-C-001 sets GIUBAR `span_end 1783874300` with **BAR floor 27 @1783841801.305** — the 16 print is 975 s post-bell; W1TT-C-002 sets URSPAL `span_end 1784042247` with **PAL floor 39 @1784042066.596**, in span. My floors were right, and the BAR example stands: at the corrected floor the book was bid 25 / ask 30, so a 27 print sits 3¢ under the ask and is not an ask-reachable low.
