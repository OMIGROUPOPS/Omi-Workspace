# INDEPENDENT AUDIT — WINDOW-1 ASYNCHRONOUS OPPORTUNITY-VS-POLICY CENSUS @ 9220eba2 — RULING: BLOCKED

**BLOCKED — time-axis measurement censoring (Item 1), an unbounded exposure class (Item 3), and orientation-row presentation (Item 4).** The census is mechanically frozen and score-free, and its committed numbers reproduce exactly — but its core construction inspects only each sibling price's **globally first** Window-1 observation and never rescans after the first leg. My corrected post-first-leg rescan from the frozen raw tape shows the damage is not marginal: **170 of 237 macro-hold naked events (71.7%) and 173 of 240 macro-micro naked events (72.1%) had a later, lawful, in-budget sibling opportunity after the actual credited first fill** — a median of ~444 qualifying episodes per recovered event — while the frozen census structurally reported them as having no such opportunity or as unverifiable "exposure without proof."

Date: 2026-07-26 · Branch: `audit/window1-independent` (child of `e6aab469`) · Auditor: independent CC session
Method: detached worktree at `9220eba26b00a5b94e86d9c644adef16382942a0`; read-only; no scoring, no candidate change, no holdout/live access; corrected census computed independently from the frozen normalized tape (nonself books + positive-size prints) as audit evidence only.

## Lineage and mechanical audit — all PASS

Sole additions-only child of exactly `53eaf2b5` (27 additions, zero modifications — all inherited strategy/result/scorer/candidate/instrument blobs unchanged). D=804 per candidate (`immutable_population_events_per_candidate`); 24/24 artifact hashes reproduce; no scorer or benchmark ran; D/C/PC/IC/S and performance fields null throughout; forbidden-access receipt corroborated. Evidence laws verified in code/data: price reach survives unproved five-contract capacity (`cumulative_five_gate_on_price_reach: false`; the capacity-unproved terminal class exists); capacity derives from chronological executed volume and is separate from reach (distinct ledger fields); positive d2 allowed inside combined headroom (`headroom_d2_max`/`strict_combined_budget`); no IC or simultaneous-pair gate (`individual_negative_gate: false`, `simultaneous_pair_evidence_required: false`); strict-ask and true-print provenance separate; prints never substituted for BBO; carried last-trade retains provenance and is never a print or BBO authority; same-timestamp sibling evidence excluded (`strictly_later`); post-boundary evidence excluded (window bounds per leg); no future information inside any row **except** the Item-1/Item-3 defects below.

## ITEM 1 — Global-first-X vs first-X-after-first-leg: **BLOCK (proven and quantified)**

Code: lines 1246–1274 iterate `x_index[(event, sibling_leg, price)]` whose `first_observation_timestamp` is the **globally first** observation (the FROZEN_X_EVIDENCE_LEDGER carries exactly one observation per (event, leg, price) — no recurrence list), and admit the X only when that first timestamp is strictly later than the first-leg fact. The 9:00/10:00/11:00 case fails exactly as described: the 9:00 observation is inspected, rejected as not-later, and the 11:00 recurrence is **never discovered** — no rescan exists anywhere.

Corrected recomputation from the frozen tape (normalized nonself books for strict-ask evidence `X > ask` and contemporaneous bids; positive-size true prints for `X ≥ print`; d1 from the **actual credited fill** vs the latest prior bid; `b2_max = floor(−d1−1)`; strict `d1+d2 < 0`; strictly-later timing):

| | macro_hold | macro_micro |
|---|--:|--:|
| naked events (actual credited first leg) | 237 | 240 |
| **with a later lawful in-budget sibling opportunity** | **170 (71.7%)** | **173 (72.1%)** |
| qualifying post-first-leg episodes (total / median per recovered event / max) | 189,437 / ~444 / 17,467 | 201,296 / ~446 / 17,467 |
| median elapsed time to first recovery | ~3.75 h | ~3.76 h |
| median first-recovery d2 | −1 | −1 |
| **sibling X-levels rejected because the global first observation was earlier, having a valid later in-budget recurrence** | **2,718** | **2,773** |

Per-event detail (event ID, episode count, d1, b2_max, first-recovery timestamp/type/min-X/bid/d2, elapsed seconds, rejected-recurring X-levels) is enumerated for all 343 recovered events in `CORRECTED_EVENT_LEVEL_CENSUS.json`. Manual spot-verification on six events confirmed the arithmetic directly against the tape (e.g., AVEFOR: d1=+2, b2_max=−3, best post-fill sibling print sits 25¢ inside budget). **This is time-axis measurement censoring: the frozen census cannot see roughly seven of every ten naked events' later opportunities.**

## ITEM 2 — Macro direction may never censor micro divots: **violated via Item 1's construction**

The census does not gate on macro labels directly, but the single-global-first-observation model deletes every repeated visit to X — precisely the divots/pullbacks/retouches the Vault doctrine protects. The corrected scan treats every tape point as a chronological episode and recovers opportunities across **all four categories** (recovered naked events: ATP_CHALL 98/101, ATP_MAIN 22/22, WTA_CHALL 22/22, WTA_MAIN 28/28 per candidate) — including rising, falling, and mixed paths; no direction label was consulted, and none suppressed a local divot. "Genuinely no observed later opportunity" is lawful for the residual 67/67 naked events only after this exhaustive scan — the frozen census's equivalent claim was not lawful, because its scan was not exhaustive.

## ITEM 3 — Unbounded "policy exposed without execution proof": **BLOCK (code-confirmed)**

Lines 1344–1360: `potential_exposures_without_evidence` counts any sibling price with **no observation at all** and `policy_ever_exposed_X` **ever** true. It checks none of the five requirements — not post-first-leg timing, not the contemporaneous combined-headroom budget, not lawful contemporaneous BBO, not remaining-Window-1 overlap; only the absence of execution proof is real. The committed counts reproduce exactly — macro-hold naked 229, no-fill 617; macro-micro naked 231, no-fill 623 (1,700 orientation rows in this terminal class overall) — and **zero of them are verified compliant with the five requirements**, because the code never evaluates them. The class as frozen is unlawful as an opportunity claim in either direction (it can both overstate and understate); survival counts belong to the corrected census.

## ITEM 4 — Orientation rows are not event counts: **defect confirmed; corrected union supplied**

Reproduced exactly: the decisive table's **474 / 672 / 480 / 680 orientation rows cover 237 / 336 / 240 / 340 distinct events** (`orientations_retained_per_event: 2`) — doubled diagnostics presented without a deduplicated event-level answer. Both orientations are retained (correct as diagnostics), but no realized-orientation primary answer and no event-level union exist in the frozen artifacts. Corrected event-level answers (score-free diagnostics; both orientations preserved in the receipt):

1. **Of 237 macro-hold naked events: 170** had a later lawful in-budget sibling opportunity after the actual credited first fill.
2. **Of 240 macro-micro naked events: 173.**
3. **Of 336 macro-hold no-fill events: 257** had an asynchronous counterfactual pair path under either retained orientation (**253 under both, 4 under exactly one**).
4. **Of 340 macro-micro no-fill events: 261** (**257 both, 4 one**).

No-fill category split (either-orientation): ATP_CHALL 168/172, ATP_MAIN 13/13, WTA_CHALL 57/57, WTA_MAIN 19/19. The no-fill paths are counterfactual (free choice of first-leg X and timing) and must never be read as realized misses; the naked-event recoveries are anchored to the real credited fill and timestamp.

## Event-level split status

Computed here: recovered-opportunity presence, episode counts, elapsed time, first-recovery d2, categories, orientation union/both/one. Requiring the corrected census (not computable lawfully from the frozen artifacts): the per-episode policy-exposure state (never exposed / moved away / exposed-with-proof-uncredited / exposed-without-proof under the five requirements), because the frozen policy ledger binds exposure only to the single global-first observation timestamp. That join is part of the required correction.

## RULING

**BLOCKED.** Narrow required correction (not implemented here): (1) replace the global-first-X admission with the earliest qualifying **post-first-leg** observation per sibling X — i.e., a full post-first-leg rescan of the chronological tape (books and prints) with per-episode contemporaneous BBO, budget, capacity, and policy-exposure joins; (2) constrain `policy_exposed_without_execution_proof` to exposures satisfying all five requirements (post-first timing, in-budget price, lawful contemporaneous BBO, remaining-corridor overlap, no proof during that exposure); (3) publish event-level primary answers (realized orientation for naked; deduplicated union for no-fill) alongside the retained orientation diagnostics, never presenting orientation-row totals as game counts. The corrected census must be re-frozen and independently audited.

This audit validates no strategy, score, benchmark, deployment, or live mutation; the corrected numbers above are measurement evidence only, and the no-fill union is explicitly counterfactual.
