# OMQS — P4b: SHAPE-SEQUENCED REPLAY (the doctrine's policy) 2026-07-02

**Policy tested (never before):** per pair, favorite = higher-mid leg at T-4h. **Favorite bid worked EARLY (T-8h→T-4h, ask−offset, pre-rise), dog bid worked LATE (T-2h→T-0, after decline)** — each postability-gated (two-sided, spread ≤6¢, depth≥1), held to T-0. Same fill model (trade ≤ target OR ask descends ≤ target). Read-only, 26JUL01 ITF slate (318 paired).

## Result — shape-sequencing does NOT rescue ITF completion
| policy | scored | **completion** | achieved ≤97/98-100/>100 | strand (which side) |
|---|--:|--:|--:|---|
| fav-early / **dog-late** (main) | 134 | **3/134 = 2%** | 1 / 1 / 1 | 31 (23%) — **dog-stranded 22**, fav 9 |
| fav-early / **dog-static-T4h** (variant) | 180 | **10/180 = 6%** | 3 / 5 / 2 | 47 (26%) — **fav-stranded 28**, dog 19 |
| current-box counterfactual (t20m cancel) | — | 1-5% | — | — |
| static-simultaneous baseline (P4) | — | **0%** | — | — |

- **All tested policies complete ≤6% on ITF:** static-simultaneous 0% (P4), sequential-divot unlicensed (P2, touch diverges r 0.47), shape-sequenced 2%, variant 6%.
- Timing doesn't fix the fill problem — the off-phase leg strands (dog strands when posted late; fav strands in the variant). The ≤97 combined is *quotable* (P3b 90%) but **unfillable as a completed pair.**

## Verdict — ITF is a PAPER OPPORTUNITY across the static/sequenced policy space
The quotable-≤97 early window (P3b) does not convert to completed pairs under any static or shape-sequenced policy. This is the structural negative the operator's two-problem frame predicts on a thin, seesaw tier: you can *see* a cheap combined but cannot *complete* it.

## The one untested ingredient — bid-walk (gates a hard close)
Every replay here is **no-walk** (post once, hold). The **live bot walks** (`v4_move_repost`) and *did* complete some ITF pairs in the deploy box (`OMQS_DEPLOYBOX_CURRENT`). So my no-walk models **systematically understate completion** — which is why even the current-box counterfactual reads 1-5% here. The relative null is robust (no static/sequenced timing wins), but the **absolute "ITF unfillable" needs a walk-augmented replay** to confirm.

## Decision (per operator's three options: build / close / re-spec)
- **Not a build:** no static/sequenced policy clears a viable completion threshold (all ≤6%).
- **Close vs re-spec hinges on walk:** the static/sequenced space is exhausted (closure per §0A invariant 5). The single remaining lever is **bid-walk** — the shadow should **re-spec to add walk** (the decisive test), and if walk-augmented ITF also fails to complete above threshold, **CLOSE the ITF pair-build** as a paper opportunity (companion to the ATP_MAIN closure). Plex's call.

Method: `p4b.py`. Baselines from `OMQS_P4_SHADOW.md` (static 0%), `OMQS_P2_SEESAW_TOUCH.md` (sequential unlicensed), `OMQS_P3B_PRET4H_SHAPE.md` (≤97 quotable 90%).
