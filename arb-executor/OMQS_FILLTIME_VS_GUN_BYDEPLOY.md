# OMQS — FILL-TIME vs the GUN, per deploy (are we filling early enough to catch the B4 drift?)

Population: all filled+settled legs, boxed by fill ET date into deploy windows (SS4C). GUN = tape volume-onset (first two consecutive >=5-trade/min windows) per leg, computed from Kalshi /markets/trades (server-side for pre-Jun24, local for Jun24-30). fill-vs-gun in minutes (negative = before gun). B4 = A50 dip window = final hour before the gun (onset-60..onset). n=2619 legs w/ computable onset. Read-only.

## (1) fill-time relative to the GUN, per deploy
| deploy | n | median | p25 | p75 | >60min pre (before B4) | 0-60min pre (in B4) | after gun (in-play) |
|---|--:|--:|--:|--:|--:|--:|--:|
| 0_preJun19 | 1312 | -292 | -378 | -250 | 96% | 1% | 4% |
| 1_Jun19-25 | 690 | -272 | -312 | -244 | 94% | 1% | 5% |
| 2_Jun26-28green | 161 | -283 | -354 | -248 | 94% | 0% | 6% |
| 3_Jun29 | 248 | -285 | -383 | -247 | 96% | 1% | 4% |
| 4_Jun30 | 208 | -276 | -336 | -248 | 96% | 0% | 4% |

## (2) median fill-vs-gun (min) by cell-price x deploy (do favorites fill later?)
| deploy | <=25 | 26-50 | 51-75 | >=75 |
|---|--:|--:|--:|--:|
| 0_preJun19 | -313 (n=199) | -289 (n=481) | -296 (n=466) | -280 (n=166) |
| 1_Jun19-25 | -264 (n=105) | -275 (n=267) | -268 (n=231) | -278 (n=87) |
| 2_Jun26-28green | -295 (n=29) | -282 (n=49) | -295 (n=56) | -272 (n=27) |
| 3_Jun29 | -262 (n=41) | -300 (n=87) | -280 (n=86) | -305 (n=34) |
| 4_Jun30 | -267 (n=35) | -274 (n=80) | -286 (n=72) | -299 (n=21) |

## (3) EARLY (>60min pre-gun) vs LATE fills: W1/corridor band-reach (Jun26+ legs w/ window data)
| group | n | W1-reach | CORRIDOR-reach |
|---|--:|--:|--:|
| EARLY (>60min pre-gun) | 516 | 7% | 17% |
| LATE (<=60min pre / in-play) | 17 | 12% | 0% |
(LATE n is tiny -- almost nothing fills late -- so the early-vs-late reach comparison is not powered; the point is that ~nothing fills late at all.)

## (4) B4-resting
- Overall (n=2619): filled >60min BEFORE the gun (already committed before B4) = **95%** | filled DURING B4 (0-60min pre) = **0%** | filled after the gun (in-play) = **4%**.
- i.e. essentially **0%% of fills land in the B4 dip window**; we are filled ~4.7h earlier and holding a non-dip price before the A50 dip ever happens.

## VERDICT — we fill TOO EARLY, not too late, and every deploy does the same
Across EVERY deploy window (pre-Jun19 -> Jun30), the median fill lands **~280 minutes (~4.7 hours) BEFORE the gun**, p25 ~-350min, p75 ~-250min. **95%% of fills happen >60min before the gun -- i.e. BEFORE the B4 final-hour dip window A50 says the dip lives in. ~0%% fill during B4.** We post at window-open (T-4h) and get hit by the first sparse premarket flow almost immediately, committing the position hours before the B4 dip. So we do NOT catch the B4 drift -- we have already filled (at the early, non-dip price) long before it. Favorites are NOT slower: their median fill-vs-gun (~-280 to -305) is indistinguishable from cheap legs -- everything fills ~4.7h early. NO deploy solved this; the fill-timing is a constant of the whole 45-day arc, unchanged by any flag. The lever this exposes: to catch the B4 dip (a LOWER fill = more room to the +band = a reachable exit), the bid must REST into the final hour rather than fill on the first premarket print -- the opposite of the current behavior. This is an entry-TIMING lever (when the bid is allowed to fill), distinct from entry-PRICE (fill vs mid, already shown clean) and from the exit-geometry favorite residual.

## PER-DEPLOY x CELL detail rows are the tables above; per-leg fill-vs-gun in deploy_rows.json (2619 legs).