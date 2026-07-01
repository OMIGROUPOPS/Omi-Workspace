# OMQS — COMPLETION FUNNEL below the pairing floor (4 main cats, Jun 24–30)

Read-only, no config touched. Reconstructed from the order-event log (posts, entry fills, match-live cancels) + authoritative Kalshi REST fills/settlements. PAIRABLE = event where BOTH legs had a posted buy-yes bid (the both-legs-anchored set, the funnel below the 79.34% PAIRING_DIAGNOSTIC floor). COMPLETED = both legs actually FILLED (REST truth). Dollars = Kalshi settlement realized. WTA_CHALL absent (near-zero pairable volume in the window).

## MEASUREMENT 1 — completion rate + failure modes (dollar-weighted)
| cat | pairable | completed | completion% | (a) stranded | (b) missed-both | (c) gun-cancel | forfeit-completion $ |
|---|--:|--:|--:|--:|--:|--:|--:|
| ATP_MAIN | 111 | 83 | 75% | 18 | 2 | 8 | **−$30.42** (a −23.16 / c −7.26) |
| WTA_MAIN | 114 | 83 | 73% | 17 | 3 | 11 | **−$4.20** (a +0.08 / c −4.29) |
| ATP_CHALL | 181 | 128 | 71% | 22 | 14 | 17 | **−$16.02** (a −12.55 / c −3.47) |
| **TOTAL** | **406** | **294** | **72%** | **57** | **19** | **36** | **−$50.65** |

Failure modes: **(a) stranded** = one leg filled, sibling never filled, no gun-cancel (queue-starve, Nishiwaki class); **(b) missed-both** = zero legs filled ($0, no position); **(c) gun-cancel** = one leg filled then sibling CANCELLED by match-live before it filled (SHINIS class, grace-off).

By dollar: **(a) queue-starve strand = −$35.63** (the biggest pot: ATP_MAIN −23.16 + ATP_CHALL −12.55); **(c) gun-cancel = −$15.02**; **(b) missed-both = $0**.

### ►► FORFEITED-COMPLETION DOLLARS = −$50.65 ◄◄
(realized loss on the 93 stranded singles that rode without their pair; a completed pair would have locked instead)

## MEASUREMENT 2 — combined-at-fill on COMPLETED pairs (dollar-weighted)
| cat | completed n | locked ≤100 | marginal 100-105 | shit >105 | forfeit-lock $ |
|---|--:|--:|--:|--:|--:|
| ATP_MAIN | 83 | 67 | 16 | 0 | $0.90 |
| WTA_MAIN | 83 | 70 | 13 | 0 | $0.70 |
| ATP_CHALL | 131 | 104 | 24 | 3 | $3.85 |
| **TOTAL** | **297** | **241 (81%)** | **53** | **3** | **$5.45** |

Combined>100 rate by fav-leg fill bucket (does overpaying the fav concentrate it?): **≤50¢ fav: 0/6 = 0% · 51-75¢: 36/205 = 18% · ≥75¢: 20/86 = 23%.** Yes — over-par completions concentrate in the higher fav-leg-fill buckets (monotone 0→18→23%), but the magnitude is tiny: 81% of completed pairs already lock ≤100, only 19% are marginal/shit, and the total over-par amount is small.

### ►► FORFEITED-LOCK DOLLARS = −$5.45 ◄◄
(sum of (combined−100) on the 56 completions that filled above par)

## THE DECISION — which build lands first
**The two pots are −$50.65 (completion-execution) vs −$5.45 (over-par pricing) — a ~9× gap.** The money is in GETTING THE SECOND LEG FILLED, not in fav-leg placement modulation:
- 81% of completed pairs already lock ≤100 — combined-price is largely SOLVED; the over-par residual is $5.45.
- The −$50.65 forfeit is the 28% of pairables that DON'T complete: 57 queue-starve strands (−$35.63) + 36 gun-cancels (−$15.02) + 19 missed-both ($0).
- **BUILD COMPLETION-EXECUTION FIRST.** Within it, the ranking is: (a) queue-starvation on the second leg = −$35.63 (biggest — the sibling sits behind the wall, Nishiwaki class), then (c) grace-off gun-cancel = −$15.02 (the SHINIS class — re-arm grace / hold the resting sibling at the gun). Fav-leg placement modulation (Measurement 2) is a −$5.45 problem — defer it.

Caveats: pairable reconstructed as both-legs-posted (≈ both-anchored); completion% (72%) is the funnel BELOW the 79.34% pairing floor; dollars use settled legs (newest legs still settling); WTA_CHALL near-zero volume.
