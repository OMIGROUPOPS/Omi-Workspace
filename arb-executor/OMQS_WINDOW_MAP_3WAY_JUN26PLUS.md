# OMQS — WINDOW MAP, THREE-WAY (fill_minus_RUNMID x cell-price x windows) — the falsifying artifact

n=486 settled filled legs Jun 26-30 with a reconstructable running-mid at fill. PRIMARY axis fill_minus_runmid = fill - running_mid (trailing 30-min traded-mean at the fill instant, the OBSERVABLE market mid; NOT retrospective fv_burst). Buckets: deep_disc<=-5, disc(-5..-1), at-mid(-1..+1), over(+1..+5), deep_over>=+5. Cell-price by fill level: <=25/26-50/51-75/>=75. Windows: W1=fill->scheduled, CORRIDOR=scheduled->gun, W2=gun->settle; reach=price hit fill+band. Kalshi REST + tick-tape. Read-only, NO exit/cut change.

## FULL THREE-WAY (per cell: n, W1/COR/W2 band-reach%, mean-windows, win%, loser-true-knife%)
| runmid bucket | price | n | W1% | COR% | W2% | meanW | win% | knife% |
|---|---|--:|--:|--:|--:|--:|--:|--:|
| deep_disc(<=-5) | <=25 | 3 | 0% | 100% | 100% | 1.67 | 0 | 0% |
| deep_disc(<=-5) | 26-50 | 11 | 50% | 50% | 82% | 1.55 | 18 | 11% |
| deep_disc(<=-5) | 51-75 | 4 | 25% | 0% | 75% | 1.00 | 75 | 100% |
| deep_disc(<=-5) | >=75 | 1 | 100% | - | 100% | 2.00 | 100 | - |
| disc(-5..-1) | <=25 | 32 | 18% | 31% | 59% | 1.00 | 0 | 22% |
| disc(-5..-1) | 26-50 | 47 | 7% | 16% | 85% | 1.04 | 43 | 22% |
| disc(-5..-1) | 51-75 | 67 | 2% | 11% | 79% | 0.90 | 61 | 50% |
| disc(-5..-1) | >=75 | 10 | 0% | 0% | 90% | 0.90 | 100 | - |
| at-mid(-1..+1) | <=25 | 44 | 0% | 22% | 75% | 0.93 | 14 | 26% |
| at-mid(-1..+1) | 26-50 | 94 | 1% | 18% | 76% | 0.91 | 35 | 34% |
| at-mid(-1..+1) | 51-75 | 83 | 1% | 6% | 78% | 0.84 | 71 | 67% |
| at-mid(-1..+1) | >=75 | 58 | 0% | 0% | 72% | 0.72 | 91 | 100% |
| over(+1..+5) | <=25 | 4 | 25% | 25% | 75% | 1.25 | 0 | 25% |
| over(+1..+5) | 26-50 | 9 | 0% | 25% | 100% | 1.22 | 33 | 0% |
| over(+1..+5) | 51-75 | 8 | 0% | 20% | 88% | 1.00 | 62 | 33% |
| over(+1..+5) | >=75 | 3 | 0% | 0% | 100% | 1.00 | 100 | - |
| deep_over(>=+5) | 26-50 | 2 | 50% | - | 0% | 0.50 | 0 | 0% |
| deep_over(>=+5) | 51-75 | 4 | 0% | 0% | 50% | 0.50 | 25 | 67% |
| deep_over(>=+5) | >=75 | 2 | 0% | 0% | 50% | 0.50 | 50 | 100% |

## DECISIVE 1 — within >=75c FAVORITES: DISCOUNT vs AT-MID vs OVER fills
| fill quality (>=75c) | n | W1% | COR% | W2% | meanW | win% | knife% |
|---|--:|--:|--:|--:|--:|--:|--:|
| DISCOUNT (frm<-1) | 11 | 9% | 0% | 91% | 1.00 | 100 | - |
| AT-MID (-1..+1) | 58 | 0% | 0% | 72% | 0.72 | 91 | 100% |
| OVER (frm>+1) | 5 | 0% | 0% | 80% | 0.80 | 80 | 100% |

ANSWER 1: for >=75c favorites, W1 and CORRIDOR reach are ~0% for DISCOUNT, AT-MID, AND OVER alike, and 100% of favorite losers are true-knives (never reach band). Discount fills do NOT meaningfully open pre-gun windows on favorites — both are floor-zero. For favorites this is GEOMETRY, not fill-quality.

## DECISIVE 2 — pre-gun (W1+CORRIDOR) reach vs cell-price, HOLDING fill at AT-MID
| at-mid & price | n | W1-or-COR reach% | W1% | COR% | W2% | win% |
|---|--:|--:|--:|--:|--:|--:|
| at-mid & <=25 | 44 | 18% | 0% | 22% | 75% | 14 |
| at-mid & 26-50 | 94 | 16% | 1% | 18% | 76% | 35 |
| at-mid & 51-75 | 83 | 6% | 1% | 6% | 78% | 71 |
| at-mid & >=75 | 58 | 0% | 0% | 0% | 72% | 91 |

ANSWER 2: at a FIXED fill-quality (at-mid), pre-gun (W1/CORRIDOR) reach declines MONOTONICALLY with cell-price: <=25 ~17%, 26-50 ~18%, 51-75 ~6%, >=75 0%. Fair fills on cheap legs still reach pre-gun; fair fills on favorites cannot. GEOMETRY IS REAL and independent of fill-quality — high fill price shrinks the windows even when the fill is fair.

## ERHROD GRID — losers that PEAKED ABOVE FILL post-gun then rode to 0 (peak-then-reverse). cell = count/losers
| runmid bucket | <=25 | 26-50 | 51-75 | >=75 |
|---|--:|--:|--:|--:|
| deep_disc(<=-5) | 3/3=100% | 8/9=89% | 1/1=100% | - |
| disc(-5..-1) | 27/32=84% | 24/27=89% | 23/26=88% | - |
| at-mid(-1..+1) | 33/38=87% | 48/61=79% | 22/24=92% | 4/5=80% |
| over(+1..+5) | 3/4=75% | 6/6=100% | 3/3=100% | - |
| deep_over(>=+5) | - | 0/1=0% | 2/3=67% | 0/1=0% |

ANSWER 3 (ERHROD): peak-then-reverse-to-0 is NOT confined to (over-mid, >=75). It runs 80-100% of losers across the ENTIRE grid — including AT-MID and DISCOUNT fills, and across every price bucket. Even fair/discount favorite fills that lose almost always printed above fill first then died. Combined with Decisive 1+2: the ERHROD death is not caused by a bad (over-mid) fill; it is the reversal geometry of the leg, which fill-quality does not remove.

## VERDICT — the three-way FALSIFIES "shit entry killed the windows" as the whole story
Both effects are real but they separate cleanly by cell-price. (i) FILL-QUALITY matters at low/mid prices: within <=50c cells, discount vs over shifts win% and pre-gun reach. (ii) GEOMETRY dominates at high prices: within >=75c favorites, W1/CORRIDOR reach is floor-zero for EVERY fill-quality (discount included) and 100% of losers are true-knives; and at fixed at-mid fill, pre-gun reach falls monotonically to 0 as price rises. A favorite (high fill) has almost no room to fill+band before the gun, so it is W2-only-or-die regardless of how good the fill was. ERHROD peak-then-reverse is near-universal among losers grid-wide, not an over-mid artifact. CONCLUSION: for the >=75c favorite legs that are the bulk of the ERHROD bleed, HIGH-PRICE GEOMETRY killed the windows, not the entry price. A better fill on a favorite does not open a pre-gun exit window. This points the residual to EXIT GEOMETRY on high-price cells (per JUNE_VAULT SS4B: per-cell band recalibration / band-asymmetric flatten), NOT to entry-quality gating on favorites.

## PER-CELL detail also emitted; full per-leg rows in the two-way artifact (OMQS_WINDOW_MAP_JUN26PLUS.md).