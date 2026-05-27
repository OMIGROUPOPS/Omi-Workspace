# ATP_MAIN paired-N — joint-cash objective: max P(both hit) x (R_fav+R_dog) — 2026-05-27

Read-only, local. 1,907 paired ATP_MAIN events, joined by `event_ticker` (fav = higher anchor). raw_max hits. **Objective per (fav_band,dog_band): choose (R_fav,R_dog) maximizing `P(both legs hit within match) x (R_fav + R_dog)`** — a non-separable joint objective (vs the prior E[A+B]).

## ⚠️ Key finding: this objective does NOT uniformly bias shallower
Across 35 band-pairs: **mean (R_fav+R_dog) = 42.3 vs v6's 32.7 (DEEPER on net, not shallower)**; mean both-hit rate **57.6% vs v6 59.9% (slightly LOWER)**. 23/35 pairs drop *one* leg shallower — but typically push the *other* leg much deeper, so the net R-sum rises and joint-fire falls.

**Why:** the `(R_fav+R_dog)` factor is linear and unbounded while `P(both) ≤ 1`. So whenever a deeper R buys more R-sum than it loses in joint-fire probability, the product rewards going deeper — the opposite of "shallow + reliable." Example: fav 72–74/dog 26–28 moves to (4, **41**) — a deep dog R that drops both-hit 86%→47% but the 45c R-sum wins the product. The objective trades joint-fire reliability *for* R-depth, not against it.

**If the real intent is shallow + reliable joint fire, this formula is the wrong lever.** Better objectives: maximize `P(both)` subject to `R_fav+R_dog ≥ floor`; or `P(both) x min(R_fav,R_dog)`; or cap R range. Flagging before any use — say which and I'll re-run.

**Same overfit caveats as the prior paired analysis:** per-pairing N=15–111 with a 45×45 sweep → the deep picks (R 41/45 on small underdog subsets) are in-sample lottery tails; not deployable as-is.

## Per band-pair: v6 vs joint-cash-optimal (outcome split = neither / one / both)

| fav band | dog band | N | v6 (R_f,R_d) | v6 both | v6 split (none/one/both) | opt (R_f,R_d) | opt both | opt split (none/one/both) | obj v6 | obj opt |
|---|---|---|---|---|---|---|---|---|---|---|
| 62-64 | 38-40 | 111 | (8,1) | 89% | 0%/11%/89% | (35,1) | 65% | 1%/34%/65% | 8.03 | 23.35 |
| 86-89 | 10-16 | 89 | (11,6) | 57% | 7%/36%/57% | (10,6) | 72% | 0%/28%/72% | 9.74 | 11.51 |
| 59-61 | 41-42 | 83 | (24,26) | 42% | 0%/58%/42% | (38,7) | 57% | 0%/43%/57% | 21.08 | 25.48 |
| 67-68 | 33-35 | 75 | (2,24) | 69% | 0%/31%/69% | (2,41) | 56% | 0%/44%/56% | 18.03 | 24.08 |
| 77-79 | 23-25 | 72 | (14,22) | 50% | 0%/50%/50% | (20,12) | 64% | 0%/36%/64% | 18.00 | 20.44 |
| 72-74 | 26-28 | 66 | (3,3) | 86% | 0%/14%/86% | (4,41) | 47% | 0%/53%/47% | 5.18 | 21.14 |
| 69-71 | 31-32 | 64 | (17,12) | 64% | 0%/36%/64% | (28,14) | 58% | 0%/42%/58% | 18.58 | 24.28 |
| 55-56 | 45-46 | 63 | (33,39) | 22% | 0%/78%/22% | (2,45) | 57% | 0%/43%/57% | 16.00 | 26.86 |
| 80-82 | 20-22 | 63 | (1,52) | 38% | 0%/62%/38% | (1,40) | 43% | 0%/57%/43% | 20.19 | 17.57 |
| 72-74 | 29-30 | 62 | (3,26) | 50% | 0%/50%/50% | (2,43) | 42% | 0%/58%/42% | 14.50 | 18.87 |
| 52-54 | 49-51 | 61 | (11,3) | 79% | 0%/21%/79% | (1,45) | 66% | 0%/34%/66% | 11.02 | 30.16 |
| 83-85 | 17-19 | 61 | (15,54) | 21% | 13%/66%/21% | (14,16) | 61% | 0%/39%/61% | 14.71 | 18.20 |
| 65-66 | 36-37 | 59 | (33,3) | 58% | 0%/42%/58% | (1,39) | 63% | 0%/37%/63% | 20.75 | 25.09 |
| 90-94 | 5-9 | 54 | (2,63) | 24% | 0%/76%/24% | (1,45) | 31% | 0%/69%/31% | 15.65 | 14.48 |
| 90-94 | 10-16 | 53 | (2,6) | 81% | 0%/19%/81% | (6,18) | 51% | 2%/47%/51% | 6.49 | 12.23 |
| 52-54 | 47-48 | 47 | (11,11) | 77% | 0%/23%/77% | (45,9) | 57% | 0%/43%/57% | 16.85 | 31.02 |
| 57-58 | 43-44 | 47 | (18,3) | 77% | 0%/23%/77% | (4,45) | 57% | 0%/43%/57% | 16.09 | 28.15 |
| 75-76 | 26-28 | 45 | (8,3) | 82% | 0%/18%/82% | (1,45) | 42% | 0%/58%/42% | 9.04 | 19.42 |
| 57-58 | 45-46 | 43 | (18,39) | 42% | 0%/58%/42% | (1,45) | 60% | 0%/40%/60% | 23.86 | 27.81 |
| 59-61 | 43-44 | 39 | (24,3) | 69% | 0%/31%/69% | (37,1) | 72% | 0%/28%/72% | 18.69 | 27.28 |
| 59-61 | 38-40 | 38 | (24,1) | 82% | 0%/18%/82% | (38,3) | 68% | 0%/32%/68% | 20.39 | 28.05 |
| 55-56 | 47-48 | 34 | (33,11) | 50% | 0%/50%/50% | (43,1) | 76% | 0%/24%/76% | 22.00 | 33.65 |
| 62-64 | 36-37 | 33 | (8,3) | 91% | 0%/9%/91% | (35,3) | 67% | 0%/33%/67% | 10.00 | 25.33 |
| 65-66 | 33-35 | 30 | (33,24) | 27% | 0%/73%/27% | (33,1) | 77% | 0%/23%/77% | 15.20 | 26.07 |
| 69-71 | 33-35 | 30 | (17,24) | 60% | 0%/40%/60% | (18,30) | 53% | 0%/47%/53% | 24.60 | 25.60 |
| 75-76 | 23-25 | 30 | (8,22) | 60% | 0%/40%/60% | (23,11) | 70% | 0%/30%/70% | 18.00 | 23.80 |
| 83-85 | 10-16 | 30 | (15,6) | 23% | 10%/67%/23% | (14,10) | 70% | 0%/30%/70% | 4.90 | 16.80 |
| 69-71 | 29-30 | 27 | (17,26) | 41% | 0%/59%/41% | (1,41) | 59% | 0%/41%/59% | 17.52 | 24.89 |
| 65-66 | 38-40 | 26 | (33,1) | 81% | 0%/19%/81% | (33,19) | 54% | 0%/46%/54% | 27.46 | 28.00 |
| 80-82 | 17-19 | 26 | (1,54) | 46% | 0%/54%/46% | (5,45) | 50% | 0%/50%/50% | 25.39 | 25.00 |
| 77-79 | 20-22 | 24 | (14,52) | 29% | 0%/71%/29% | (10,45) | 42% | 0%/58%/42% | 19.25 | 22.92 |
| 62-64 | 41-42 | 22 | (8,26) | 64% | 0%/36%/64% | (12,45) | 50% | 0%/50%/50% | 21.64 | 28.50 |
| 49-51 | 49-51 | 19 | (3,3) | 95% | 0%/5%/95% | (3,45) | 53% | 0%/47%/53% | 5.68 | 25.26 |
| 77-79 | 26-28 | 19 | (14,3) | 79% | 0%/21%/79% | (6,45) | 47% | 0%/53%/47% | 13.42 | 24.16 |
| 67-68 | 36-37 | 15 | (2,3) | 93% | 0%/7%/93% | (9,44) | 60% | 0%/40%/60% | 4.67 | 31.80 |

## Reading the outcome split
- At the joint-cash optimum, mean outcome split is roughly: **neither 0% / one 42% / both 58%**.
- Both-cash (both legs hit their R) is the minority outcome in most pairs — the legs' anti-correlated price paths make simultaneous up-moves uncommon. Pushing R deeper (as this objective does) makes both-cash *rarer*, not more reliable.

*Read-only, local, in-sample. Objective implemented exactly as specified; the deeper-not-shallower result and overfit caveats are flagged above. v6 zone-aware per-leg R remains deployed; no change made.*