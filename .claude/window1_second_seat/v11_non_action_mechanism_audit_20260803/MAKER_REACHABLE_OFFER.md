# Maker-reachable offer — the channel split that sizes the true bar

Analysis seat only. Read-only. V48 trades-as-truth (`e073c606`). A resting bid is filled only by a **seller crossing to it** or the **ask descending onto it** — never by a **buyer lifting the ask**. This splits the traded offer into what a maker can actually reach. Machine artifact: `…/MAKER_REACHABLE_OFFER.json`.

## (1) The gap completing prints, by taker side

| gap class | seller-aggressed | buyer-lift |
|---|--:|--:|
| print above rest | 7 | 29 |
| print before rest stood | 70 | 15 |
| rest absent | 3 | 1 |

**The split re-reads the gap map.** The **PRINT_ABOVE_REST** ('we bid under') misses are **81% buyer-lifts** (29 of 36) — a buyer lifting the ask **cannot fill a resting bid**, so those were never a maker offer to sit at; the bid-under fault is largely illusory. The **PRINT_BEFORE_REST_STOOD** (ordering) misses are **82% seller-aggressed** (70 of 85) — **real maker offers that printed before the rest stood**. The true maker fault is *timing/presence*, not bidding under.

| category | seller-aggressed | buyer-lift |
|---|--:|--:|
| ATP_CHALL | 33 | 28 |
| ATP_MAIN | 11 | 5 |
| WTA_CHALL | 30 | 6 |
| WTA_MAIN | 6 | 6 |

## (2) THE MAKER OFFER — whole 804

Per leg, maker-reachable floor = **min(lowest seller-aggressed print, lowest ask-descent-dwell)**, post-first-lawful-stand; pair-sum < 100 = completable.

| offer | games completable under par |
|---|--:|
| all-comer traded offer *(V48 stated)* | **711** |
| all-comer traded offer *(my anytime measure)* | 562 |
| **THE MAKER OFFER** | **501** |
| captured (V48) | **396** |

**THE MAKER OFFER = 501** — between the 396 captured and the ~562-711 all-comer. The buyer-lift portion of the traded offer is **not maker-reachable**; strip it and the honest ceiling for a resting book is **501**, not 711.

## (3) The 700/804 bar — the arithmetic, three numbers

| lever | number |
|---|---|
| **maker offer ≥ 700?** | **NO — 501**, short by **199** |
| **presence-expansion** to close it | **+199 games** must come from earlier/more presence — but the maker-reachable universe (~562) is itself below 700, so presence alone cannot reach it |
| **selective taking** (fee math) | 65 takeable-not-maker games; **net -12¢** (locked 123¢ − taker fees 135¢); only 12 of 65 net-positive |

**Stated plainly (no recommendation):**
1. The maker offer is **501** — a resting book, perfectly run, tops out **199 short of 700**.
2. Closing that with **presence** needs **+199** games, but the maker-reachable universe (~562) is below 700 — presence cannot get there alone.
3. Closing it by **taking** the buyer-lift/pre-stand offers is **fee-negative**: over the 65 takeable games the taker fees (135¢) **exceed** the locked margin (123¢), net **-12¢**; the margins at these prices do not clear the fee — only 12 games survive it.

The three numbers say the 700 bar is not reachable maker-only, not by presence to its ceiling, and not profitably by taking. The true bar the tape supports for a resting book is the **maker offer, ~500**.

## Conservation

804 games. Captured 396 · THE MAKER OFFER 501 · all-comer anytime 562 (V48 stated 711). Gap completing prints by side: PRINT_ABOVE seller 7/buyer 29, PRINT_BEFORE seller 70/buyer 15, REST_ABSENT seller 3/buyer 1. 700-bar: maker 501 (−199); presence +199; taking 65 games net -12¢ (12 survive fees). Fee law ceil(0.07·p·(100−p)/100)/contract. Source V48 e073c606, prints/tapes fit-local, closes 57daf3c1.