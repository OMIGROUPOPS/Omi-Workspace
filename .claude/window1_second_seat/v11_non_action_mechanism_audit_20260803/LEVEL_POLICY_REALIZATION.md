# Level-policy realization — the last free variable

Analysis seat only. Read-only. 3-channel causal fills (`084df125`), riser legs **T5-armed** (first two-sided book), faller legs fixed at their causal floor. **Realized** capture: a maker rest fills at **the level it actually occupied when the flow arrived** (a trade/seller-print ≤ R, or the ask ≤ R dwelling ≥10 s) — not the best-case reachable. Beside the **collectable bar 632 / 5,217¢** (the T5 causal ceiling). Machine artifact: `…/LEVEL_POLICY_REALIZATION.json`.

## The four policies

- **P1** bid−1 tracking (V36 incumbent) — rest 1¢ under the bid every receipt.
- **P2** persistent-level join, persistence-only ≥300 s (the `2b45d146` law with the seller-hit gate **removed** per the frontier) — hold the deepest level that has rested 300 s; no rest before the first join.
- **P3** = P2 + bid−1 tracking **before** the first join.
- **P4** = P3 + during a transient-dip signature (fresh-ask <60 s dwell + bid-heavy book, the measured 336-class signal) hold the deeper of the current level and the running excursion low.

## Realized capture vs the 632 / 5,217¢ collectable bar

| policy | completable | under-par | locked ¢ | % of bar | ≤93/≤95/≤97/<100 | riser forfeits |
|---|--:|--:|--:|--:|---|--:|
| **P1 bid−1 tracking [V36]** | 417 | **410** | **3442** | 66% | 86/125/217/410 | 239 |
| **P2 persistence-only join** | 521 | **480** | **3493** | 67% | 83/120/206/480 | 117 |
| **P3 join + bid−1 between** | 521 | **480** | **3495** | 67% | 83/120/206/480 | 117 |
| **P4 + transient-dip hold** | 521 | **480** | **3498** | 67% | 83/120/207/480 | 117 |

**The join is the realized winner and the refinements are inert.** P1→P2 jumps +70 completed pairs and **halves riser forfeits (239→117)** by holding persistent levels bid−1 chases past. But **P3 and P4 add ~nothing** (3493→3495→3498¢, same 117 forfeits): once you hold a deep join you cannot also track bid−1 for transient punches with a single rest.

**Every policy tops out near 3,500¢ — ≈67% of the 5,217¢ collectable bar.** The remaining **~1,700¢ is collectable but not realizable**: occupying the exact level at the exact moment, without foreknowledge, is the binding constraint. bid−1 and join capture *different* flow (transient punches vs persistent levels) and no single-rest policy holds both.

## Per category — under-par (locked ¢): P1 vs P2

| category | P1 under-par | P1 ¢ | P2 under-par | P2 ¢ |
|---|--:|--:|--:|--:|
| ATP_CHALL | 174 | 1145 | 201 | 1159 |
| ATP_MAIN | 96 | 595 | 102 | 552 |
| WTA_CHALL | 69 | 1278 | 87 | 1321 |
| WTA_MAIN | 71 | 424 | 90 | 461 |

## Named — which policy realizes what

| leg | anytime | causal (T5) | P1 bid−1 | P2 join | P3 | P4 |
|---|--:|--:|--:|--:|--:|--:|
| **ARN** | 50 | 56 | 56 | None | None | None |
| **COP** | 47 | 47 | None | 64 | 64 | 64 |
| **VRB** | 68 | 68 | 73 | None | None | None |
| **WES** | 60 | None | None | None | None | None |
| **NIK** | 18 | 18 | 19 | 29 | 29 | 29 |

- **ARN — no policy realizes 50.** The deep-50 flow passed before any lawful rest could occupy 50 (persistence needs 300 s; the trades came first). Best realized is **56 via bid−1**; the join, held at 50, sits *below* the only remaining 56 flow and never fills. 50 is a ceiling artifact, not realizable.
- **COP — join realizes 64, bid−1 nothing.** COP's bid persisted at 64; the join holds and fills there. The transient 47 (the causal reach) is unrealizable — no rest ever occupied 47 when the lone trade hit.
- **VRB — bid−1 realizes 73, join never arms.** No 300 s-persistent fillable level, so the join is null; bid−1 tracks up and catches 73. The causal 68 is not realized.
- **NIK — bid−1 (19) beats join (29).** bid−1 tracks down to the deep transient at 19 (near the causal 18); the join sits at the shallower persistent 29. Here the incumbent wins.
- **WES — realized by nothing** (all null): no persistent level, no bid−1 catch; the anytime 60 collapses to zero realized.

The named split cleanly: **bid−1 catches transient punches (ARN 56, VRB 73, NIK 19); the join catches persistent levels (COP 64).** Neither dominates, and P3/P4 cannot fuse them — the core reason realized capture stalls at ~67% of collectable.

## Conservation

409 riser legs, 637 games; faller floors fixed. Collectable bar 632/5217¢ (T5 ceiling). Realized under-par/locked: P1 410/3442 · P2 480/3493 · P3 480/3495 · P4 480/3498. Riser forfeits P1 239 · P2–P4 117. Machinery 084df125, sealed union 57daf3c1, divot census d1ac9497.