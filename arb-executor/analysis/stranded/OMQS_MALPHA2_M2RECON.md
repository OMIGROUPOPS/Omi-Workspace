# OMQS — M-α2: M2 RECONCILIATION under pair-completion (2026-07-01)

**Question:** the M2 gun-cancel (`v4_t20m_fallback` stale-buffer cancel) was ruled **protective** under the *naked band-capped exit* — filling those 81 flow-through bids netted **−$24.62** (winner capped at +band, loser rides to 0). Does that cost survive under **PAIR-COMPLETION** economics (complete the pair, hold both to settle, combined ≤97/≤100)? **Gate: pair-completion neutralizes the M2 cost (≤ +$10/day).**

## Result — YES, pair completion neutralizes it
Reconstructed the flow-through set: `order_cancelled label=v4_t20m_fallback` bids where a `taker_side="no"` print later hit at/through the cancelled bid.

| set | n | sibling-filled |
|---|--:|--:|
| this reconstruction (Jun20-30, loose window) | 405 | 328 |
| doc's Track-2a 81-set (narrower window) | 81 | 64 |

**⚠ Scope caveat:** my set is a **superset** of the doc's 81 (broader dates + a looser "any taker-no ≤ bid after cancel" rule) — so the absolute dollar below is **not a clean like-for-like** with the doc's −$24.62. The *per-event economics* (below) are scale-invariant and that's the transferable finding.

### Pair-frame vs naked-frame (sibling-filled 328)
| frame | NET | combined buckets |
|---|--:|---|
| naked band-capped (published, doc's 81) | **−$24.62** | — |
| **pair-completion (winner-independent, this set)** | **−$5.30** | ≤97: **46** · 98-100: **221** · >100: **61** |

- **M2-cost delta ≈ +$19** — completing pairs moves the flow-through economics from **strongly-negative-naked to ~neutral-pair.**
- **Mechanism:** a completed pair pays 100¢ regardless of which leg wins, so the **exit asymmetry** (winner capped at +band, loser rides to 0) that produced the −$25 **disappears**. The fills land **mostly at par** (221/328 = 67% in 98-100), only 14% clear ≤97, 19% over-par.

### Verdict
**M2 is NO LONGER protective under pair completion.** Its protective value came entirely from dodging fills that fed the asymmetric naked exit; once we complete pairs, those same fills are **~breakeven (−$5), not −$25**. So the **M2 protective-cancel does not block the don't-pull / always-lay fix** — the gate condition (pair-frame cost ≤ +$10/day) is met.

**Consistent with M-α1:** completing is **neutral, not +EV** — most completions are at par, not good prices. Fixing the cancel stops it from *dodging* now-neutral fills; it does not create profit.

Method: `malpha2.py`; per-event flip table `malpha2_flips.json`. Baseline −$24.62 from `OMQS_MEASUREMENTS_2026-06-30.md` (M2).
