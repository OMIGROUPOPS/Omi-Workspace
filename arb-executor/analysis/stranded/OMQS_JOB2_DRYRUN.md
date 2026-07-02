# OMQS — JOB-2 DRY-RUN (KNOWN-CONTAMINATED pipeline shakeout, 2026-07-01)

**⚠ NOT DECISION DATA.** Pre-re-anchor timing (premarket window bounded on the STALE scheduled start, which P1 just showed is off by a wide/multimodal +24-to-+81 min). This exercises the corrected-frame scoring pipeline on (i) + (iii) only; **(ii) window-reachability is DEFERRED to the post-P1 re-derivation.**

## (i) combined-≤97 achievability CEILING under sequential best-divot fills
Per pair, best-case = the lowest `taker_side=no` print on each leg in the (stale) premarket window, summed (a perfect-divot-catch upper bound; real fills are worse). 31 pairs had both legs with a premarket sell-print:
| bucket | n | % |
|---|--:|--:|
| **≤97 (good)** | 6 | **19%** |
| 98-100 (par) | 23 | 74% |
| >100 (fail) | 2 | 6% |

By cat: ATP_MAIN 0% ≤97 (all par) · WTA_MAIN 25% · ATP_CHALL 25% (17% >100) · ITF_M 33% · ITF_W 0%.

**Shakeout read (not a decision):** even at the CEILING (perfect divot-catch on both legs), only **~19%** of pairs reach ≤97 — most (74%) top out at par. Consistent with the whole arc: the ≤97 good-price target is structurally hard; pairs are par-bound even at best. Real (imperfect, single-divot) fills will clear ≤97 far less often.

## (iii) throughput floor (≥25 fills/day)
From `OMQS_DEPLOYBOX_COMPARE`: CURRENT deploy (flags OFF) ~44 fills/day (~69 outage-adjusted) → **above floor**; PRIOR (flags ON) ~354/day → far above. Floor is not the binding constraint in either config.

## (ii) window-reachability — BLOCKED
Requires tape-relative W1/corridor/W2 boundaries, which per P1 need re-derivation (not a shift). Deferred.

Method: `jobdry.py`. Sample ≤40/cat paired events with scheduled starts.
