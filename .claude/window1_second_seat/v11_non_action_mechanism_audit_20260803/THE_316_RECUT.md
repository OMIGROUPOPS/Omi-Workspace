# The 316 re-cut — union law, no seller-cross privilege

Analysis seat only. Read-only. Every leg the autopsy stamped **L6** (present-but-no-counterparty + over-par) re-cut under the CANON three-channel law with **no seller-cross privilege**. Lowest available in the post-lawful-rest span = `min(lowest dwelled ask ≥10 s, lowest traded print, lowest seller-cross)` = the **causal reach** (`causal_own_reach_low`, which correctly excludes pre-trigger flow). Verdict vs our rest. Machine artifact: `…/THE_316_RECUT.json`.

*(The pre-L5-recut L6 stamp was 316; the corrected L6 set re-cut here is **342**.)*

## The verdict — the market's 'no' was almost never real

| verdict | legs | share |
|---|--:|--:|
| **REST_BELOW_AVAILABLE** (we sat under the offer) | **209** | 61% |
| **REST_AT_AVAILABLE** (reachable, not credited) | **121** | 35% |
| **TRULY_NOTHING** (empty book) | **12** | 4% |
| **total** | **342** | |

**Only 12 of 342 (4%) are truly the market's no.** The other **330 had a takeable offer** and V45 captured **0** of them — a **0/330 capture rate against the tape's real offer** on this residual.

## The fault ledger, re-cut

- **209 PLACEMENT FAULTS** — we sat **under** the market's lowest offer by k = median **1¢** (p75 2¢, max 3¢). A 1-3¢ greed/sanity gap: the bid never rose the last cent to the offer.
- **121 CREDITING FAULTS** — the lowest available was **at or below our rest**, i.e. the price was reachable, yet the leg is uncredited. **This is the seller-cross privilege**: the offer arrived as a **traded print or a dwelled ask** (never a seller-cross — see below), and V45's crediting demanded a seller-cross that never came. Drop the privilege and these credit.
- **12 TRULY_NOTHING** — no ask ever descended, nothing traded, no cross. The genuine empty book.

## The channel that set the lowest — no seller-cross privilege, confirmed

Across the offered legs the lowest available was set by **TRADED_PRINT (142) or DWELLED_ASK (109)** — **SELLER_CROSS set it on zero legs**. The market's real offer never *needs* a seller to cross to the bid; an ask descending and dwelling, or any trade at the level, is the offer. V45's seller-cross-only crediting discards it.

## Per category (verdict counts)

| category | REST_BELOW | REST_AT | TRULY_NOTHING |
|---|--:|--:|--:|
| ATP_CHALL | 109 | 60 | 6 |
| ATP_MAIN | 23 | 20 | 3 |
| WTA_CHALL | 51 | 27 | 0 |
| WTA_MAIN | 26 | 14 | 3 |

## The over-par re-sum

On the honest (causal) channel, **0 of 146** over-par games sum < 100 — **the over-par set is genuinely over-par**; the tape's real offers still don't cross par. (The earlier wrong-arm scan wrongly flipped 24; correcting the arm to the lawful-rest time removes them.) So the over-par L6 verdict survives; the NO_COUNTERPARTY verdict does not.

## Corrected totals

- **The tape's true offer:** 330 of 342 L6 legs had a takeable price; 12 empty.
- **V45's true capture rate against it:** **0 / 330** on this residual.
- **Fault ledger:** 209 placement (sat 1-3¢ under) + 121 crediting (seller-cross privilege) + 12 truly market-no.

## Named

| leg | rest | causal (lowest available) | verdict |
|---|--:|--:|---|
| **SALIBR·IBR** | 43 | 44 | REST_BELOW_AVAILABLE by 1¢ |
| **LUZTSE·TSE** | 79 | 79 | REST_AT_AVAILABLE |
| **SURECH·SUR** | 47 | 48 | REST_BELOW_AVAILABLE by 1¢ |
| SURECH·ECH | 52 | null | CHAIN_L4_LATE_POST — outside the L6 set |

- **SALIBR·IBR — REST_BELOW_AVAILABLE by 1¢.** The ask dwelled at **44¢ for ~15 h**; our rest sat at **43¢**, one cent under. Not a market-no — a **1¢ placement gap at the sanity floor** (a maker cannot bid at the resting ask). The 44¢ was on offer the entire window; we were a cent shy.
- **LUZTSE·TSE — REST_AT_AVAILABLE.** The causal offer reached **79¢ = our rest**; the price was reachable but the leg is uncredited — the dwelled/traded 79 never came as a seller-cross, so V45's privilege refused it. A **crediting fault**, not a market-no.
- **SURECH·ECH — outside the re-cut** (CHAIN_L4_LATE_POST, causal null: the deep join armed 75 s before the edge). Its partner **SUR is REST_BELOW by 1¢** (rest 47, offer 48).

## Conservation

342 L6 legs re-cut, each one verdict (sum 342): REST_BELOW 209 + REST_AT 121 + TRULY_NOTHING 12. True offer existed on 330; V45 captured 0. Over-par re-sum 0/146. k median 1¢. Channel: traded-print / dwelled-ask only, seller-cross never. Source V45 3bda0a54, causal reach d3db740f, closes 57daf3c1.