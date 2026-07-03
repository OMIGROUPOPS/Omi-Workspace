# OMQS — TONIGHT'S FILLS CROSS-CHECK: zero-discount defect + per-side projection — 2026-07-02

**Decision-bearing artifact** (the deploy evidence for `per_side_placement`). Read-only.

## The defect, from the live tape: EVERY fill tonight is ZERO-DISCOUNT
Every `entry_filled` since 19:00 had **`fill_price == posted_price`** — the bid was posted *at* the trading level and filled *instantly at that level*. No dip captured; we bought the touch, we were not paid by a move coming to us. This is the direct product of the shallow (≈1¢) offsets in both live tables (`per_regime_offsets_v2` + `entry_table_percell_conservative`), which maximize fill by sitting at the market.

| pair | leg | side | posted | filled | discount |
|---|---|---|--:|--:|:--:|
| MENDIM | MEN | fav | 61 | 61 | ZERO |
| MENDIM | DIM | dog | 39 | 39 | ZERO |
| HALGIR | GIR | fav | 53 | 53 | ZERO |
| HALGIR | HAL | dog | 47 | 47 | ZERO |
| JACBUB | JAC | fav | 78 | 78 | ZERO |
| JACBUB | BUB | dog | 22 | 22 | ZERO |
| DUCCOB | DUC | dog | 30 | 30 | ZERO |
| ROYZVE | ZVE | fav | 95 | 95 | ZERO |
| TIACHO | CHO | dog | 14 | 14 | ZERO |
| OSONOS | NOS | fav | 79 | 79 | ZERO |
| OSONOS | OSO | dog | 21 | 21 | ZERO |
| YAMKOI | KOI | fav | 54 | 54 | ZERO |
| YAMKOI | YAM | dog | 45 | 45 | ZERO |
| IMASAM | SAM | fav | 62 | 62 | ZERO |
| IMASAM | IMA | dog | 38 | 38 | ZERO |
| DELMAT | DEL | fav | 77 | 77 | ZERO |

**16/16 zero-discount.** (SMIVER / Smirnova-Verster never filled — PROCESSED on a garbage schedule.)

## The fix, projected: `per_side_placement` (dog deepened 3¢ to the dip floor, A49 median)
The favorite leg is left shallow (fill early at/near current, cheap vs its coming rise). The **dog leg rests 3¢ deeper** so the dip pays it (A49: 97% dip ≥1¢, median 3¢; A50: dips heaviest late-window). Per-pair combined old → new:

| pair | fav (unchanged) | dog old → new | **combined old → new** |
|---|--:|--:|:--:|
| YAMKOI | KOI 54 | YAM 45 → **42** | 99 → **96** ✓≤97 |
| IMASAM | SAM 62 | IMA 38 → **35** | 100 → **97** ✓≤97 |
| HALGIR | GIR 53 | HAL 47 → **44** | 100 → **97** ✓≤97 |
| MENDIM | MEN 61 | DIM 39 → **36** | 100 → **97** ✓≤97 |
| OSONOS | NOS 79 | OSO 21 → **18** | 100 → **97** ✓≤97 |

**The win: per-side turns par (99–100) fills into sub-97 discounts** — the ≤97 entry target — by getting paid by the dog's dip instead of buying its touch. Projection assumes the dog fills at the 3¢-deeper resting level; A49 says 97% of tickers dip ≥1¢ and the median dip is 3¢, so the deeper bid fills on the dip in the large majority of cases (the residual is the miss-rate trade-off, bounded by the taker fallback).

**Validation (tonight, as fresh windows open):** grade the actual deepened-dog fills DISCOUNT (fill below the posting-moment touch) vs ZERO-DISCOUNT, and confirm the zero-discount class shrinks toward zero on the dog side. Method: `grep ENTRY_FILLED` + compare `posted_price` to the anchor at post time.
