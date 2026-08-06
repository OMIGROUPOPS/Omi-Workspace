# Rest sanity census + spread regime map — the BEFORE table  ·  V34-W1 (e56d79a2)

Analysis seat only. Read-only. 1,608 legs, V34-W1 causal decision trace
(`order_after_cents` = standing rest vs `observation.bid` = live best bid) + seller-
aggressed prints from `prints.jsonl`. Machine artifact:
`.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/REST_SANITY_SPREAD_REGIME_BEFORE.json`.

## The verdict in one line

The no-chase rest parks **1c under an early low bid and never chases up**, so it sits a
**median 29¢ below the live best bid** for the whole span, **69% of legs can never take**
(spread never tightens), **half never reach the deepest seller-hit**, and a trivial
1c-under-live-bid tracking rest would have been in the path of **1,044 of 1,787 seller-hit
sweeps the frozen rest sat out**.

## (a) Gap between the standing rest and the contemporaneous best bid

| | median | p90 | max |
|---|--:|--:|--:|
| per-leg **median** gap (bid − rest) | **29¢** | 68¢ | 94¢ |
| per-leg **p90** gap | 34¢ | 72¢ | 95¢ |

A properly tracking rest (1c under best bid) has gap = 1. The observed median leg sits
**29 cents** under the live bid. The rest is not near the market.

## (b) Deepest seller-hit — touched or not

**Not touched: 785 / 1,608 (49%).** On half the book, the rest's highest level never
reached the leg's deepest seller-aggressed print — the cheapest fill the tape offered
was structurally out of the rest's range. Touched: 823.

## (c) Spread ≤ 1 regime — the take-path's lawful window

**MAKER-ONLY legs (spread ≤ 1 for < 1% of the W1 span): 1,113 / 1,608 (69%).** For more
than two-thirds of legs the take path — which needs a ≤1¢ spread to lift a qualified ask
— is essentially never lawful. Those legs *must* be won on the resting bid, which makes
the mis-placement in (a)/(b) fatal, not cosmetic.

## (d) Seller-hit sweeps and the tracking-bid counterfactual

Sweeps (≥3 seller-aggressed hits across ≥3 descending levels within 60s):
**1,787 sweeps across 235 legs.** A bid **tracking 1c under the current best bid,
cap-bounded**, would have been in the path of **1,044 (58%)** of them — caught by the
descending sweep — whereas the frozen rest, stuck 29¢ low, was in the path of far fewer.
1,044 missed sweep-fills is the recoverable surface a tracking rest unlocks.

## Structural failures

- **Rest never entered the active range (rest_max > 10¢ below bid_max): 475 / 1,608
  (30%).** Nearly a third of legs, the rest was never within 10¢ of where the market's
  bid traded — it sat idle the entire span.
- **Placement absurdities (rest stuck, gap p90 ≥ 10¢, *and* deepest seller-hit never
  touched): 329.** Emblematic: `ROUGAN-GAN` rest parked at **3** while its **cap was 94**
  and a seller sold at **94** — gap p90 **95¢**. `KHOVIG-KHO` rest 3, seller-hit 98, cap
  96. `RABRUS-RUS` rest 1, seller-hit 94. The rest is at the floor of the book while the
  fill it needed printed at the ceiling.

## Distributions per category (conservation 1,608)

| category | legs | gap median (leg-median) | maker-only | deepest not-touched | never-active | sweeps | tracking-bid in path |
|---|--:|--:|--:|--:|--:|--:|--:|
| ATP_CHALL | 738 | 22¢ | 524 (71%) | 387 | 202 | 767 | 356 |
| WTA_MAIN | 304 | 30¢ | 222 (73%) | 120 | 101 | 337 | 248 |
| ATP_MAIN | 294 | 37¢ | 197 (67%) | 116 | 88 | 450 | 304 |
| WTA_CHALL | 272 | 27¢ | 170 (63%) | 162 | 84 | 233 | 136 |
| **all** | **1,608** | **29¢** | **1,113 (69%)** | **785** | **475** | **1,787** | **1,044** |

## Reading

This is the **BEFORE** table. It isolates *why* the V34 bleed census found 190
REST_STARVED + 90 STATE_MISLABEL: the rest is not badly *timed*, it is badly *placed* —
frozen 1c under a stale early bid, a median 29¢ below the live market, on a book that is
69% maker-only so the take path can't rescue it. The single change the numbers point to
is a rest that **tracks 1c under the current best bid, cap-bounded** — it would enter the
path of 1,044 sweeps and reach the deepest seller-hit on the 785 legs that never did.
The AFTER table measures that fix.

## Conservation

1,608 legs censused (1,604 carry trace observations; 4 no-trace). Sums: maker-only 1,113
+ 495 take-capable = 1,608. Deepest-hit touched 823 + not-touched 785 = 1,608. Sweeps
1,787 total, 1,044 tracking-in-path, across 235 legs.
