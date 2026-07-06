# B3 DISCOUNT COUNTERFACTUAL — the rode legs vs their own lows (2026-07-06 17:17:01 ET)

**Read-only, findings only. Conservative fill convention: a maker bid at X counts FILLED only where the tape PRINTED ≤X in-window; single-print lows sub-flagged (queue risk). Honest clock; windows from the ledger (hs_ts / cor_end_ts). band_x at counterfactual fills = empirical per-(cat, 10¢-bucket) median from this session's own v4_exit_posted records (47 cells) — deployed behavior measured, nearest-bucket fallback stated.**

## Prior art (C45) + the delta
- **T47/Path-B shallow-offset verdict** — card-era, pre-live: cannot pre-rule this live measurement (date caveat stated).
- **A49** (aim = fillable dip) · the July missed-divot ledger · **ONE_AIM_FIX Job-1 POPSAN** (the pair existed only at the divot) · census: fills land 11–34min before the dip (per-leg gauge later struck; the joint gap stands).
- **DELTA: first band-touch conversion replay on the live B3 rode population, honest clock — and the first pre-T-4h look (the Vault's PRE-T-4H-NEVER-EXAMINED debt).**

Population note: the book regenerated since the 42-pair cross-tab; this run finds **50 rode legs in B3-shape pairs (44 tape-covered, 6 no-usable-window/tape — named, excluded from conversion math)**. Gold comparison set: 58 legs (w1_filled AND cashed W1/COR, tape-covered).

## 1 · The missed discount (per-leg table at bottom; distributions here)

- fill_actual − LOW_T4: **med 11.0¢ [p25 -2.0 – p75 23.0]**, max 54.0¢
- the low printed AFTER our fill on 28/44 legs (med 5.0min) — we bought, then it got cheaper; 16 lows printed before our fill (we were late to a dip already gone)
- single-print lows (queue-risk flag): 19/44

## 2+3 · Counterfactual band-touch × fillability — BOTH lanes, the NET

| depth | filled (tape-backed) | converts W1 | converts COR | no-convert (rides at cf basis) | Δ$ vs actual (NET, all lanes) |
|---|---|---|---|---|---|
| LOW | 44/44 (by construction — the low printed; queue-risk flags above) | 2 | 10 | 32 | **+53.15** |
| LOW+1 | 44/44 (by construction — the low printed; queue-risk flags above) | 3 | 10 | 31 | **+51.30** |
| LOW+2 | 44/44 (by construction — the low printed; queue-risk flags above) | 3 | 8 | 33 | **+40.42** |

**The honest number: even filled AT their own lows, 32/44 rode legs NEVER see their band pregame — the conversion wing is 12 legs. The +$53 NET is mostly cheaper-basis riding (smaller losses), not cashing. The discount is HALF the recipe: it cuts the bleed ~40% but does not manufacture band-touches.** Fillability lane: 6 legs had no usable W1 tape at any depth (the true un-fillable class).

## Pair-level effect at LOW: B3 → what
12 of the B3 pairs gain a pregame-cashed leg at LOW → those pairs re-grade B3→B1/B2 (sibling dispositions already cashed in 12 cases); the remaining pairs stay B3 at reduced basis.

## 4 · T-8H EXPANSION — the pre-T-4h debt, first look
- Coverage: **29/44 rode legs have recorder tape reaching T-8h→T-4h; 545 prints total in that band** (prints = trades, not quotes; premarket_ticks quote depth unexamined here — stated).
- Of covered legs, 27 printed in T-8h→T-4h at all; additional discount LOW_T4 − LOW_T8: med -6¢ [p25 -18 – p75 0] (positive = the earlier window was CHEAPER).
- per cat: ATP_CHALL: med -1¢ (n=12) · ITF_M: med -13¢ (n=4) · ITF_W: med -7¢ (n=4) · WTA_CHALL: med 0¢ (n=5) · WTA_MAIN: med 1¢ (n=2)
- Additional converts at T-8h lows: not computed as converts — the T-8h band-touch replay needs exit cells for those levels and longer windows; this look establishes COVERAGE and DISCOUNT only (the debt is now sized, not settled).

## 5 · THE COMMON-DENOMINATOR TABLE — gold vs rode, same columns

| column | GOLD (n=58) | RODE (n=44) |
|---|---|---|
| fill − LOW_T4 ¢ | 4.0 [1.0–11.0] | 11.0 [-2.0–23.0] |
| low timing vs fill min (+ = low after fill) | 29.1 [0.2–84.0] | 5.0 [-82.8–34.4] |
| band distance from LOW ¢ | 7 [4–13] | 7 [4–13] |

**The read, off the distributions:** gold missed its lows by med 4.0¢ and rode by med 11.0¢ — gold caught its lows and rode missed: the recipe is the one number — discount-to-low.

**Integration with §2 (both true, stated together):** the 7¢ gold-vs-rode separation says the discount-to-low is the strongest single separator between the classes — but §2 caps its power on THIS population: filled at their own lows, only 12/44 rode legs' bands ever printed pregame. The discount explains who ENDS UP gold; it converts only the ~quarter of rode legs whose bands eventually arrived. The other three quarters are the census-§7 sibling/band-arrival story, not an entry-depth story.

## Per-leg raw (rode)

| ev | cat | fill | LOW_T4 | miss ¢ | low vs fill min | 1-print? | cf@LOW conv | Δ$@LOW | LOW_T8 |
|---|---|---|---|---|---|---|---|---|---|
| RMATCH-26JUL06BASHOE | ATP_CHALL | 46.0 | 40 | 6.0 | 2.0 | Y | NO | +0.60 | 50 |
| RMATCH-26JUL06ERHSIN | ATP_CHALL | 4.0 | 5 | -1.0 | -24.4 |  | NO | -0.05 | 4 |
| RMATCH-26JUL06MARBER | ATP_CHALL | 39.0 | 41 | -2.0 | -214.3 |  | NO | -0.10 | 42 |
| RMATCH-26JUL06MARHAM | ATP_CHALL | 92.0 | 95 | -3.0 | -213.0 | Y | NO | -0.15 | 96 |
| RMATCH-26JUL06MAXGHI | ATP_CHALL | 54.0 | 52 | 2.0 | 1.0 | Y | NO | +0.20 | 53 |
| RMATCH-26JUL06NIJRAH | ATP_CHALL | 40.0 | 11 | 29.0 | 276.4 | Y | NO | +1.45 | 42 |
| RMATCH-26JUL06OPIPET | ATP_CHALL | 28.0 | 11 | 17.0 | 26.5 |  | NO | +0.85 | 27 |
| RMATCH-26JUL06PERMEL | ATP_CHALL | 1.0 | 5 | -4.0 | -237.7 |  | NO | -0.20 | 5 |
| RMATCH-26JUL06RAQRIB | ATP_CHALL | 36.0 | 41 | -5.0 | -104.0 | Y | NO | -0.50 | 35 |
| RMATCH-26JUL06SEGBRA | ATP_CHALL | 61.0 | 28 | 33.0 | 28.8 |  | COR | +3.40 | 64 |
| RMATCH-26JUL06VILBOC | ATP_CHALL | 22.0 | 25 | -3.0 | -204.4 |  | NO | -0.30 | — |
| RMATCH-26JUL06WEIGRA | ATP_CHALL | 16.0 | 20 | -4.0 | -82.8 |  | NO | -0.20 | 19 |
| RMATCH-26JUL06ZORDEV | ATP_CHALL | 55.0 | 39 | 16.0 | 5.7 |  | NO | +1.60 | 54 |
| FMATCH-26JUL06ALIMIS | ITF_M | 4.5 | 7 | -2.5 | -32.3 |  | COR | +0.85 | — |
| FMATCH-26JUL06DUHCAR | ITF_M | 12.0 | 1 | 11.0 | 41.4 |  | NO | +0.55 | — |
| FMATCH-26JUL06ELDHAU | ITF_M | 65.0 | 56 | 9.0 | 5.0 | Y | NO | +0.45 | 69 |
| FMATCH-26JUL06GARCIO | ITF_M | 41.0 | 2 | 39.0 | 90.2 |  | COR | +2.06 | 47 |
| FMATCH-26JUL06LENTHE | ITF_M | 32.0 | 32 | 0.0 | -0.0 | Y | COR | -0.20 | — |
| FMATCH-26JUL06LENTHE | ITF_M | 65.0 | 11 | 54.0 | 177.7 | Y | NO | +2.70 | — |
| FMATCH-26JUL06LUEVAN | ITF_M | 74.0 | 61 | 13.0 | 20.9 |  | COR | +9.61 | — |
| FMATCH-26JUL06TEUHAS | ITF_M | 30.0 | 1 | 29.0 | 43.3 | Y | NO | +2.90 | 39 |
| FMATCH-26JUL06TISVER | ITF_M | 53.0 | 5 | 48.0 | 63.1 |  | COR | +2.85 | — |
| FMATCH-26JUL06VULCOU | ITF_M | 16.0 | 1 | 15.0 | 237.5 |  | NO | +0.75 | 7 |
| WMATCH-26JUL06BOSTOP | ITF_W | 27.5 | 14 | 13.5 | 42.1 |  | COR | +3.15 | 36 |
| WMATCH-26JUL06BOWMAT | ITF_W | 8.0 | 12 | -4.0 | -16.8 |  | W1 | +0.60 | — |
| WMATCH-26JUL06CENBUL | ITF_W | 20.0 | 1 | 19.0 | 90.5 | Y | NO | +0.95 | — |
| WMATCH-26JUL06DRISLA | ITF_W | 36.0 | 12 | 24.0 | 34.4 |  | COR | +2.00 | — |
| WMATCH-26JUL06GANPUI | ITF_W | 12.5 | 12 | 0.5 | 1.5 |  | NO | +0.05 | 19 |
| WMATCH-26JUL06LUKNOE | ITF_W | 69.0 | 56 | 13.0 | 20.4 | Y | NO | +0.65 | 74 |
| WMATCH-26JUL06MCAENC | ITF_W | 42.0 | 17 | 25.0 | 32.0 |  | NO | +2.50 | — |
| WMATCH-26JUL06OKUPRI | ITF_W | 56.0 | 33 | 23.0 | 68.4 | Y | NO | +1.15 | — |
| WMATCH-26JUL06PACLOV | ITF_W | 52.0 | 52 | 0.0 | 0.1 | Y | NO | +0.00 | 56 |
| WMATCH-26JUL06SINUSU | ITF_W | 62.0 | 46 | 16.0 | 8.1 | Y | NO | +0.80 | — |
| WMATCH-26JUL06TRIVOR | ITF_W | 89.0 | 66 | 23.0 | 21.8 | Y | NO | +1.15 | — |
| WMATCH-26JUL06URREVA | ITF_W | 60.0 | 33 | 27.0 | 21.0 |  | NO | +2.70 | — |
| RMATCH-26JUL06ARANIL | WTA_CHALL | 24.0 | 26 | -2.0 | -238.1 |  | COR | +1.50 | — |
| RMATCH-26JUL06BASBAD | WTA_CHALL | 25.0 | 25 | 0.0 | -199.2 | Y | NO | +0.00 | 25 |
| RMATCH-26JUL06BOUKOT | WTA_CHALL | 20.0 | 23 | -3.0 | -260.0 | Y | COR | +1.30 | 23 |
| RMATCH-26JUL06HERNGU | WTA_CHALL | 58.0 | 37 | 21.0 | 6.8 | Y | NO | +1.05 | 56 |
| RMATCH-26JUL06HESPAL | WTA_CHALL | 69.0 | 62 | 7.0 | 3.2 |  | NO | +0.35 | — |
| RMATCH-26JUL06NOHBUR | WTA_CHALL | 75.0 | 60 | 15.0 | -180.9 | Y | W1 | +4.60 | 78 |
| RMATCH-26JUL06WERSAL | WTA_CHALL | 65.0 | 70 | -5.0 | -39.4 |  | NO | -0.25 | 68 |
| AMATCH-26JUL06KEYNOS | WTA_MAIN | 54.0 | 57 | -3.0 | -83.0 |  | NO | -0.11 | 58 |
| AMATCH-26JUL06PAOEAL | WTA_MAIN | 58.0 | 60 | -2.0 | -199.0 |  | NO | -0.11 | 59 |