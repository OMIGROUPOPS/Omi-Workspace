# AUDIT AMENDMENT — WINDOW-1 BOUNDARY HANDLING IN THE ASYNC OPPORTUNITY CENSUS AUDIT

**This amendment supersedes only the quantitative recovery/opportunity figures of my audit `d3bc4365`. It confirms Cursor Codex's fail-closed conflict, retracts the contaminated numbers, and republishes boundary-lawful counts. The frozen census `9220eba2` REMAINS BLOCKED, but the honest magnitude is far smaller than I first reported.**

Date: 2026-07-26 · Branch: `audit/window1-independent` · Additions-only child of `d3bc43650e0ad340aa6d8450ed1aa1e7d3a59481` · Auditor: independent CC session
Scope: quantitative boundary handling only. No census implemented, no candidate/tuning/scoring/holdout/live access; unrelated settled audits untouched.

## 0. Conflict independently reproduced — CONFIRMED (before anything else)

Against my own published `CORRECTED_EVENT_LEVEL_CENSUS.json`, using the frozen guarded right boundary (`boundary.guarded_cutoff_ts`, positive-provable) carried in the census's own FROZEN_X_EVIDENCE_LEDGER: **145 of 170 macro-hold and 145 of 173 macro-micro claimed naked "first recoveries" occur strictly after the guarded cutoff; only 25 / 28 were inside.** Post-cutoff excess spans **8.0 to 4,248.795 seconds**. **AVEFOR**: guarded right `1783879200`, my prior first recovery `1783880557` — **1,357 s outside Window 1**. My `d3bc4365` scan bounded evidence on the left (`policy_left_ts`) and by print-in-window for prints, but **applied no guarded right boundary to the book/strict-ask stream** and reported the globally-first post-first-leg recovery — so it admitted post-cutoff evidence. The conflict is real and mine.

## 1. Authoritative frozen boundary — cited

The passed Range-Attack/scoring lineage derives the lawful Window-1 right edge in `window1_range_attack_reference_adapter_v2.guarded_cutoff` from `REAL_START_LEDGER_V5.jsonl`, using `start_source_class` + guard band → `cutoff = anchor − positive_guard`, admitted only when `positive_window1_provable == true`. The census froze exactly these as `FROZEN_X_EVIDENCE_LEDGER.boundary.{guarded_cutoff_ts, positive_window1_provable}`. **Inclusivity preserved exactly: left inclusive `policy_left_ts`, right inclusive `≤ guarded_cutoff_ts`.** No substitution (scheduled start, raw-cache extent, last observed timestamp, or unguarded causal-action boundary) was used.

## 2–3. Boundary-applied naked-recovery rescan (during construction) — lawful counts

Rescan from frozen raw inputs with the boundary applied while building each leg's chronological stream (books and prints both clipped to `[policy_left_ts, guarded_cutoff_ts]`; events without a positive-provable boundary contribute nothing); d1 from the actual frozen credited fill vs latest prior lawful bid; `b2_max = floor(−d1−1)`; sibling evidence strictly later than the first fill and `≤` the right boundary; strict `d1+d2 < 0`; every repeated in-window visit is a distinct episode.

| | macro_hold | macro_micro |
|---|--:|--:|
| naked events | 237 | 240 |
| **lawful recovered (later in-window in-budget opportunity)** | **49** | **52** |
| total qualifying in-window episodes | 5,603 | 5,929 |
| median episodes / event · median elapsed to first lawful recovery | 36 · ~4.0 h | 35.5 · ~3.6 h |
| median first-recovery d2 | −1 | −1 |
| **X-levels: global-first predates first fill but a lawful recurrence exists strictly before the right boundary** | **117** | **124** |
| residual naked events with no observed lawful later opportunity | 188 | 188 |
| excluded for boundary unavailable | 0 | 0 |

First-recovery evidence split (macro_hold): 42 strict-ask (X > ask), 59 print (X ≥ print price) — both with contemporaneous bid; carried last-trade never used as print or BBO. **Removed solely as post-boundary evidence: 145 events per candidate.** The 49/52 survivors reconcile as 25/28 that were already inside plus 24/24 events whose only lawful recovery was an in-window recurrence my post-boundary-first scan had skipped past. By category (recovered naked, hold/micro): ATP_CHALL 10/13, ATP_MAIN 19/19, WTA_CHALL 1/1, WTA_MAIN 19/19.

## 4. No-fill counterfactual pair-path rescan (boundary-lawful) — distinct events, explicitly counterfactual

Both proposed leg episodes inside their own lawful corridors, second strictly later than first, contemporaneous d1/b2_max, strict combined negativity, no IC/simultaneous/individual gate, no post-boundary evidence:

| | macro_hold | macro_micro |
|---|--:|--:|
| no-fill events | 336 | 340 |
| **either-orientation union** | **81** | **84** |
| both orientations | 52 | 54 |
| exactly one orientation | 29 | 30 |
| neither orientation | 255 | 256 |

These remain **counterfactual** (free choice of first-leg X and timing) and are **not realized policy misses**.

## 5. Policy-exposure attribution — unavailable, not "exposed without proof"

Attribution requires all five requirements joined at one lawful episode (post-first timing; contemporaneous combined-headroom budget; lawful positive-size external BBO; remaining-corridor overlap; execution-proof presence/absence). The frozen policy ledger binds exposure only to the single global-first observation timestamp, so this join is not computable from the frozen artifacts. Every such row must be named **unavailable**, not `policy_exposed_without_execution_proof` — the frozen census's 229/617/231/623 rows in that class remain unlawful as opportunity claims (Item 3 of `d3bc4365` stands).

## 6. Manual verification — all pass

- **AVEFOR excluded**: cutoff `1783879200`, d1=2, b2_max=−3, **zero** in-window qualifying episodes, 432 post-boundary books — correctly absent from the lawful survivor set.
- **Six survivors verified against raw tape + guarded receipts**: BROHUA (strict-ask X=30 at `…3581` ≤ cutoff `…2800`), DODDEL (62), BOUGAN (66), VILGAN (8), **VUKBRO (print-based: price 41 ≤ bid 42 + b2_max −1 at `1783979002.68` ≤ cutoff `1783992600`)**, DENBAR (43) — each has a qualifying episode strictly inside its boundary.
- **Six removed post-boundary cases verified**: AVEFOR, BOUVIT, BROGIU, DELMAK, DEVGON, FANBIG — each has **zero** in-window qualifying episodes and 224–1,951 post-boundary books that my prior scan wrongly consumed.
- **Endpoint / same-timestamp / print / strict-ask**: 0 survivors have a first recovery exactly at the cutoff and 0 strictly after (inclusive right honored); same-timestamp sibling evidence excluded by strict-later; both print and strict-ask provenance admitted with separate authority.

## 7. Explicit supersession of `d3bc4365` quantitative findings

**RETRACTED (contaminated by post-boundary evidence), superseded by the lawful counts above:**

| figure | `d3bc4365` (retracted) | lawful |
|---|--:|--:|
| recovered naked events | 170 / 173 | **49 / 52** |
| no-fill event unions (either) | 257 / 261 | **81 / 84** |
| qualifying episodes | 189,437 / 201,296 | **5,603 / 5,929** |
| recurring X-levels | 2,718 / 2,773 | **117 / 124** |
| derived 559-event union | RETRACTED | superseded per-class above |

**Prior mechanical findings UNCHANGED** (not affected by the boundary error): sole additions-only child lineage, 27 additions / zero modifications, D=804, 24/24 artifact hashes, no-scorer/null-metrics, and the *structural* code findings — Item 1 global-first-X construction (lines 1246–1274, single-observation x_index, no rescan), Item 3 unbounded exposure class (lines 1344–1360, checks none of the five requirements), and Item 4 orientation-rows-are-not-event-counts (474/672/480/680 rows over 237/336/240/340 events).

## Final amended ruling

**BLOCKED — unchanged verdict, corrected magnitude.** The V1 global-first-X construction **remains structurally BLOCKED** after lawful recomputation: even within the guarded boundary, **49/237 and 52/240 naked events** recover a lawful later in-budget opportunity the frozen census could not see, and **117/124 sibling X-levels** had a lawful in-window recurrence discarded by the global-first rule. A smaller lawful effect does not cure the structural defect — but I overstated it roughly 3.5× by omitting the right boundary, and that error is retracted here. The narrow correction named in `d3bc4365` stands (post-first-leg rescan **bounded by the guarded right edge**, five-requirement exposure constraint, event-level union), now with the boundary requirement made explicit. No strategy, score, benchmark, or deployment is validated; the no-fill union is counterfactual.
