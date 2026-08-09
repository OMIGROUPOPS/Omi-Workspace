# FLOW_ABOVE_REST loosening sweep — pricing the last cent

Analysis seat only. Read-only. V41 (`96d33316`) re-scored with the rest law **raised by +k** — `rest = min(bid−1+k, cap, ask−1)`, join intact, sanity intact — applied **universally**. Fill law = V41 CANON reach-crediting; true book = locked margin + naked P&L on certified closes (the `a30f5ccd` method). **k=0 reproduces V41 exactly (243/732c/+50/782).** Machine artifact: `…/FLOW_ABOVE_REST_LOOSENING_SWEEP.json`.

## The 349 dwelled-ask levels above the rest

| gap above rest | legs | cumulative |
|---|--:|--:|
| +1¢ | 208 | 208 |
| +2¢ | 93 | 301 |
| +3¢ | 48 | 349 |

+1¢ covers **208 (60%)**, +2¢ cumulative 86%. **But only TRADE-sourced misses are maker-reachable**: raising the bid toward a dwelled *ask* above it never fills (sanity forbids resting at/above the ask — the ask must descend). Only a **trade** above the rest is caught by a raised bid; ≈155 of the +1¢ legs qualify.

## The sweep — two columns per k

| k | completed | locked ¢ | naked P&L ¢ | **true book ¢** | net Δ ¢ |
|---|--:|--:|--:|--:|--:|
| **0 (V41)** | 243 | 732 | +50 | **782** | — |
| **+1** | 281 | 799 | +34 | **833** | +51 |
| **+2** | 264 | 764 | -62 | **702** | -80 |
| **+3** | 251 | 746 | -205 | **541** | -241 |

| k | GAINED: new fills / new pairs / +locked ¢ | COST: reprice ¢ / new naked / over-par / lost ¢ |
|---|---|---|
| +1 | 155 / 38 / +76 | 30 / 85 / 0 / 0 |
| +2 | 195 / 25 / +49 | 52 / 120 / 0 / 11 |
| +3 | 206 / 14 / +34 | 75 / 138 / 0 / 17 |

**Only the first cent pays.** **+1¢ nets +51¢** true-book ($0.51/contract, +255¢ at five lots): 38 new pairs / +76¢ locked for only 30¢ of reprice. **+2¢ and +3¢ lose** (−80¢, −241¢): the naked P&L craters (+50 → +34 → −62 → −205) as raising the rest manufactures **new one-legged fills** (85 / 120 / 138 new naked exposures) — unhedged directional losers, the same CAP_UNFEASIBLE dynamic. The last cent is worth +51¢; the second and third cost the book.

## Net true-book Δ by category (vs V41)

| category | +1 | +2 | +3 |
|---|--:|--:|--:|
| ATP_CHALL | +46 | -27 | -94 |
| ATP_MAIN | -3 | +4 | -9 |
| WTA_CHALL | +7 | -29 | -81 |
| WTA_MAIN | +1 | -28 | -57 |

## Named top-20 games — the loosening misses the prizes

| game | class (census) | converted by +k? |
|---|---|---|
| **PENTHA** (58¢) | FLOW_BELOW (THA reach 20 < rest 22) | **no** — rest too shallow; raising it moves *away* from the flow |
| **KIRSEK** (55¢) | FLOW_AT_REST_PRETRIGGER (KIR reach 28 ≤ rest 30) | **no** — a timing miss; needs an earlier trigger, not a higher rest |
| **VANLEE** (46¢) | FLOW_BELOW (VAN reach 53 < rest 54) | **no** — flow ran under the rest |
| **MCKOUA** (9¢) | FLOW_BELOW (MCK reach 54 < rest 55) | **no** — flow ran under the rest |

**Every named top-value game is FLOW_BELOW or PRETRIGGER — none is FLOW_ABOVE**, so the loosening leaves them untouched. The +51¢ at +1c is earned by ~155 *small* FLOW_ABOVE-via-trade legs (low individual value); the high-value prizes need the **opposite** fix — a deeper/faster walk (FLOW_BELOW) or an earlier trigger (PRETRIGGER). Loosening is a broad-but-shallow win that does not reach the headline games.

## Conservation

804 games re-scored at k=0..3 (k=0 = V41 243/732¢/+50/782). Per k true book: +1 833 · +2 702 · +3 541 (Δ +51 / -80 / -241). 349 FLOW_ABOVE split 208/93/48; only TRADE-sourced (~155 at +1) maker-reachable. Source V41 MARKET 96d33316, certified closes 57daf3c1; join fills unrepriced, tracking fills +k, dynamic pair cap.