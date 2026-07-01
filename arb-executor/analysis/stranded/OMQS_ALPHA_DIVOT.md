# OMQS — α: MISSED-DIVOT LEDGER on stranded winners (trade-grounded, 2026-07-01)

**Question (Vault §4E-α, operator-refined):** ground the divot test in the **real missed trade prints**, not hypothetical book events. On the stranded winners, find every catchable fill we missed (a `taker_side="no"` print = someone sold YES into a bid, at/below our reference level, premarket), classify **why** we missed it, and only then ask whether a book signal *led* it. Buildable if leading-AUC>0.65 AND window>latency — **but even coinflip signals are moot if the error-class split is mechanical.**

**Verdict: α is NOT a prediction problem — it is a DON'T-PULL problem. No predictor needed.**

## The decisive finding — error-class split
16 stranded winners with both L1 tape + trade tape. **978 catchable missed prints** (taker_side=no, p ≤ our reference bid level, premarket).

**By print (fill-opportunity volume):**
| class | count | share | $-weight* |
|---|--:|--:|--:|
| **PULLED** — we had a bid ≥ p, cancelled it, then it traded | **930** | **95.1%** | 98.3% |
| TOO_DEEP — resting below the print (underpriced) | 0 | 0.0% | 0.0% |
| BEHIND_WALL — at the level but out-queued | 6 | 0.6% | 0.2% |
| NEVER_LAID — no bid on the leg at that time | 42 | 4.3% | 1.5% |

**By leg (16):** PULLED-dominant **5**, NEVER_LAID-dominant **4**, BEHIND_WALL **1**, no/few catchable prints **6**.

**Both views point away from prediction:** the missed fills are overwhelmingly **PULLED** (we abandoned a level the market then traded) and secondarily **NEVER_LAID** (we posted no bid). **TOO_DEEP = 0** — we were *never* underpriced; **BEHIND_WALL = 0.6%** — queue position is not the problem. There is nothing to *predict*; the bid simply wasn't there when the fill came.

\*$-weight is a print-frequency exposure proxy `(100−p)·min(count,5)` that over-counts beyond our 5-lot/leg cap — read the **proportions**, not the absolute ($3,339 gross).

## Catchability window vs our latency
Level-available duration around each missed print: **P50 = 0s** (many are single-tick), **P75 = 26s, P90 = 643s** (10 min), max hours. Our repost-latency proxy (median inter-repost gap) ≈ **40s**. So the upper half of dips rested **far longer than our reaction time** — they were eminently catchable had we simply **stayed on the bid**.

## Leading-signal test — moot, and reported as such
Presence in the 5s before each missed print (share, N=978; NOT an AUC vs control): depth-pull **22.8%**, ask-thin **35.2%**, quote-velocity **18.2%**, **sibling-trade 66.7%**. The sibling co-move (⅔) is consistent with the seesaw, but the buildable-AUC question is **moot**: 95% of missed fills hit a level we had already cancelled — you cannot out-predict a bid that isn't posted. **α-as-predictor is unnecessary.**

## Reconcile with cancel-timing (89%)
`OMQS_CANCEL_TIMING_JUN26PLUS` found 1,223/1,373 = **89%** of cancelled-before-start bids saw a trade at/through the bid after cancel. On this stranded-winner subset the pulled-then-touched share is **95%** — the same defect, concentrated on exactly the legs that then stranded. The stranded-winner bleed **is** the premature-cancel defect (Vault §6 gun-cancel defect / stale scheduled clock).

## What ships (mechanical, no model)
1. **Don't pull the resting premarket bid** — gate cancels on true match-start (ESPN `status=="live"` / volume-burst latch), not the stale scheduled clock. Removes the 95%-of-prints / 5-legs PULLED class.
2. **Always lay a bid on both legs** — fixes the NEVER_LAID legs (4/16). (Ties to pair_governor / the never-fired divot-catcher build preconditions in §4E.)
3. β (gun-cross) stays a **backstop only** (+$8, `OMQS_BETA_GUNCROSS.md`) — the winner is expensive by the gun; the money is upstream, keeping the cheap premarket bid alive to the divot.

**α buildable-signal (AUC>0.65 ∧ window>latency): N/A — not needed.** The recovery path is mechanical (don't-pull + always-lay), which needs no prediction. Method: `alpha.py`; per-print ledger `alpha_ledger.json` (978 rows: ts, price, our_bid, class, window, signals).
