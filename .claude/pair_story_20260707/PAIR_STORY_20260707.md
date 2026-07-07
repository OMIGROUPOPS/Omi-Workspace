# PAIR-STORY — the corpus at pair grain, tick level, honest axis (2026-07-07)

**Re-dispatch of the run the 07-06 storm killed; this artifact supersedes it (none ever landed).** Read-only, findings only, no builds.

**Universe & referee:** 3,824 tick-covered events (7,644 `premarket_ticks` 5-level files at run time) ∩ 2,737 corpus-belled events (LATCH-CAL canonical, 25m residual gate, as banked by the shape-corpus accumulator; `observed_starts` preferred where matchable — **1 match used**; the archive is 13 rows old, banking since 07-06 21:57) = **2,457 detected-bell pairs → 2,396 analyzed** (37 no-joint-fillable, 24 thin-ticks, named in `agg_counts.json`). Window T-8h→bell. Prints = `analysis/trades` tape. Ran detached (tmux `pair_story`) + watcher; producer `analysis/pair_story_20260707.py`; raw per-pair records `/root/pair_story_20260707/results.jsonl`; aggregates + plots committed alongside this doc.

**Conventions (stated):** fillable(t) = min print in the trailing 15 min (a resting bid at that level, posted earlier, fills within 15 min — the B3 conservative convention at pair grain); joint combined(t) = fav_fillable(t) + dog_fillable(t) where both exist; divot moment = minute whose min print ≤ window-low + 2¢; fav = higher first joint mid; bucket = fav first-mid 20¢ band; mids used ONLY for the seesaw/shape mechanics (0A: the buyability deliverable is prints-only); ramp = trailing print-rate ≥ 3× the T-8h→T-4h baseline sustained 15 min.

**Prior art (C45):** LIVING_VAULT front page (gold recipe tight/early/under-the-wall; B3 decomposition — discount is half the recipe; 11¢-missed-lows), SLATE_LEDGER §7 census columns, B3_DISCOUNT_COUNTERFACTUAL (leg grain, rode population), per-leg Atlas shapes (card-clock context). **Delta: PAIR-level joint buyability, tick-level seesaw, honest axis, corpus scale (2,396 pairs vs the ledger's ~100-leg populations).**

---

## §1 · JOINT BUYABILITY — the achievable-floor table (THE deliverable)

Best jointly-fillable combined per pair (conservative prints-only), distribution per cat (buckets in the appendix table below):

| cat | n | p10 | p25 | **med floor** | p75 | %≤97 | %≤95 | %≤93 | %≤90 | bestT (med, min to bell) | dwell≤97 (med min) | gap (med ¢) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **ITF_M** | 787 | 65 | 74 | **84** | 92 | **89.5** | 83.9 | 77.0 | **68.9** | **−17** | 32 | **16.0** |
| **ITF_W** | 767 | 68 | 76 | **84** | 94 | **86.0** | 80.2 | 73.0 | 64.3 | **−15** | 28 | 14.5 |
| **ATP_CHALL** | 410 | 71 | 80 | **93** | 98 | 67.3 | 59.3 | 53.2 | 45.6 | −17 | 10 | 7.0 |
| **WTA_CHALL** | 29 | 77 | 82 | **90** | 98 | 72.4 | 58.6 | 51.7 | 51.7 | −4 | 6 | 10.0 |
| **WTA_MAIN** | 219 | 79 | 90 | **99** | 100 | 36.1 | 33.8 | 31.5 | 26.0 | −85 | 0 | 1.0 |
| **ATP_MAIN** | 184 | 91 | 98 | **99** | 100 | 16.8 | 15.2 | 13.0 | 9.8 | −229 | 0 | 1.0 |

**The read: 97 is an emergency ceiling, not a target, everywhere except the mains.** The ITF canvas *typically* offers **84** — a 13-16¢ discount below the ceiling — and offers ≤90 on two-thirds of pairs, with a **~30-minute dwell** at ≤97. CHALL offers 90-93 typically. The mains' canvas is par-locked: the median pair never offers sub-99, ever (1¢ gap — the tight-book regime; the ITF gap is 15¢).

**Per-cat S-line recommendation (operator ruling: S = full W1 lifecycle at a combined that beats the wall meaningfully; A = the shape at 94–97).** Anchored at the median achievable floor — S should mean "took what the canvas typically offers," not luck:

| cat | **S-line (combined ≤)** | rationale |
|---|---|---|
| ITF_M | **≤ 84** | med floor; 77% of pairs offer ≤93, so 94-97 (A) is genuinely mid-pack here |
| ITF_W | **≤ 84** | med floor (p25 76) |
| ATP_CHALL | **≤ 93** | med floor; ≤90 available on 46% |
| WTA_CHALL | **≤ 90** | med floor (n=29, LUCK-POLLUTED n<30 — provisional until the sample grows) |
| WTA_MAIN | **≤ 93** | med offers par; S must live in the p10–p25 tail (≤93 = top ~31%) |
| ATP_MAIN | **≤ 93** | same logic; ≤93 = top 13% of what the canvas ever offers |

Buckets matter inside a cat (appendix): dog-heavy ITF_M bucket-2 med **80** vs bucket-4 med 91; ATP_CHALL bucket-4 (heavy fav) med 96 — the S-line could be bucket-refined at arm time; the per-cat line above is the conservative single number.

## §2 · DIVOT SEQUENCE — the synchrony recipe at scale

| cat | n | fav-first % | inter-divot lag med (min) | p75 | P(leg-2 divot within 15m) | 30m | 60m |
|---|---|---|---|---|---|---|---|
| ATP_CHALL | 410 | 58.0 | 64 | 243 | 18.5 | 32.0 | 48.8 |
| ATP_MAIN | 184 | 57.6 | 27 | 120 | 32.1 | 53.3 | 64.7 |
| ITF_M | 787 | 51.3 | 47 | 132 | 18.6 | 35.3 | 60.4 |
| ITF_W | 767 | 51.1 | 51 | 167 | 15.8 | 33.1 | 55.4 |
| WTA_CHALL | 29 | 55.2 | 49 | 284 | 20.7 | 34.5 | 51.7 |
| WTA_MAIN | 219 | 63.0 | 44 | 231 | 29.2 | 42.5 | 53.9 |

**The 0A sequential doctrine confirmed at corpus scale:** there is no reliable ordering (fav-first ≈ coin-flip outside WTA_MAIN's mild 63%), and the two divots are typically **~45-65 minutes apart** — only ~1 pair in 6 offers both divots within 15 minutes. Simultaneous both-leg posting at static targets forfeits nothing rare; each-leg-at-its-own-divot IS the structure. The half_timing leak (~131¢/night: the fader's dip passing before leg-1 fills) is this table's live shadow — the lag is real and exploitable only by bids RESTING through it on both legs.

## §3 · SEESAW MECHANICS — how much of one leg is readable from the sibling

1-min mid-delta cross-correlation per pair (lag 0 dominates in every cat; ±1/±5-min lags add nothing material — the inversion is SIMULTANEOUS at minute grain):

| cat | n | corr@lag0 med [p25–p75] | % strongly inverse (≤ −0.3) |
|---|---|---|---|
| WTA_CHALL | 29 | −0.84 [−0.93 – −0.66] | 89.3 |
| ATP_CHALL | 398 | −0.74 [−0.89 – −0.44] | 81.3 |
| ITF_W | 738 | −0.68 [−0.85 – −0.42] | 82.2 |
| ITF_M | 758 | −0.70 [−0.86 – −0.39] | 81.8 |
| WTA_MAIN | 218 | −0.63 [−0.89 – −0.05] | 64.3 |
| ATP_MAIN | 182 | −0.29 [−0.68 – 0.00] | 50.0 |

The seesaw (paired_mid_sum ≈ 0.998, 0A) is a *minute-grain, same-minute* phenomenon in ITF/CHALL: the sibling's tape explains most of a leg's move as it happens, not after. In ATP_MAIN the two books decouple half the time — consistent with independent deep books rather than one MM quoting both. Fill-is-information (C43) has its mechanism here: the sibling's print IS the leg's move.

## §4 · CANONICAL PAIR SHAPES + RAMP (plots: `shapes.png`, `floors.png`)

| cat | ramp detected % | ramp med (min to bell) | joint-slope pre (¢/hr) | post | best floor AFTER ramp % |
|---|---|---|---|---|---|
| ITF_M | 18.8 | −27 | **−5.3** | −2.4 | 71.6 |
| ITF_W | 19.0 | −29 | **−3.9** | −1.7 | 76.7 |
| ATP_CHALL | 8.8 | −25 | −2.0 | +0.3 | 75.0 |
| WTA_CHALL | 6.9 | −17 | −6.5 | −18.4 | 100.0 (n=2) |
| WTA_MAIN | 7.8 | −22 | −0.3 | +1.5 | 76.5 |
| ATP_MAIN | 4.3 | −43 | −0.0 | +1.1 | 37.5 |

- A sharp print-rate ramp (≥3× baseline, 15-min sustained) exists on only **~9-19%** of pairs — most books thicken gradually; the "gun" as a discrete pre-bell event is the exception, not the rule, on this detector.
- Where a ramp exists, **the achievable floor lands AFTER it ~72-77% of the time** (ITF/CHALL) — the floor is a late-corridor phenomenon.
- The joint fillable combined **converges downward into the bell** in ITF (−4 to −5¢/hr pre-ramp): the canvas cheapens as the bell approaches. Mains are flat (~0): nothing to converge to below par.
- **The drift-over-lowest-traded gap — the W1 opportunity number per cell:** med(combined mid over the window) − best joint floor = **ITF_M 16¢ / ITF_W 14.5¢ / WTA_CHALL 10¢ / ATP_CHALL 7¢ / mains 1¢** (per-bucket in the appendix: ITF_M bucket-2 = **19¢**). That is what the canvas pays a correctly-resting pair versus its own typical level.

## §5 · DOCTRINE READ (prose; no proposals)

Where the gold/S moments live: **late canvas, at or after the (usually undetectable) ramp, inside the last ~20 minutes before the bell** — median bestT is −15/−17 min in ITF/CHALL with a ~30-minute ≤97 dwell, and the floor lands after the ramp three times out of four where a ramp exists at all. The achievable floor therefore opens AFTER the ramp per cat, not before — but it is only catchable by bids that were RESTING long before it: the divots that compose it sit ~50-65 minutes apart across the two legs (§2), so the pair's floor is assembled sequentially, one leg's low at a time, exactly as 0A's inverse-aware doctrine says. This is the gold recipe's "early" resolved at pair grain: early POSITION, late FILL. The B3 finding survives contact at scale — the discount is there (the ITF canvas typically offers 84, a 13¢ beat of the ceiling, 16¢ under its own drift) but it is late, brief at its best point (dwell at ≤best+2 is minutes, dwell at ≤97 is ~half an hour), and mains offer essentially nothing below par — the two-problem frame's answer differs by cat: in ITF the entry problem is timing/patience, in the mains the canvas itself declines to pay. 97 as a goal was calibrated to the mains' reality; for ITF/CHALL it is an emergency ceiling ~13¢ above what the market typically hands a resting pair, which is precisely the S/A split the ruling drew.

---
*Hourly decomposition (coverage-first, prints vs quote-touch, mains go/no-go): `HOURLY_APPENDIX.md`.*

*Appendix — per-(cat,bucket) floors: `aggregate.json` → floors (bucket rows also printed in the run log). Re-verification: this study re-runs on the accumulating honest corpus as observed_starts coverage grows (the 1-of-2,457 bell preference today will rise; the LATCH-CAL axis is canonical until then).*
