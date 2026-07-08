# POST-GUN FORENSIC — 2026-07-08 (read-only; honest-clock era 07-06 12:00 pm ET → 07-08 ~4:30 pm ET)

**Findings only. No rule changes. All times ET.**

## Part 0 — prior art (C45)
- **LIVING_VAULT front page** — window structure W1 → gun → 5-min grace → W2/corridor; FERCER (premature cancel, 06-19) / ALCCLA (latch-blind on lying kalshi_primary clock, 07-03) lineage. Delta: this doc sizes the whole gun surface per cat instead of per-exhibit.
- **MORNING_DOSSIER 07-08** — 77% of blackout fills landed in-play (dead-bot class). Honored here: adopted-booking fills are FLAGGED OUT of the boundary read (their fill time is booking time, not fill time).
- **Gun-silent finding** — latch fires ~25% on thin books (gun_thin_shadow lineage). Reproduced and refined per cat below (17–62%).
- **HOURLY_APPENDIX + EARLY_CANVAS_PART2** — flow-state thresholds provisional; the S-line habitat (T-20m→bell) sits exactly where the latch lags land.

## Method
`postgun_forensic.py` (committed alongside; run on VPS, raw `postgun_out.txt`). Truth starts = shape-corpus tape bells (405 era events; **TAPE-DERIVED — the corpus accumulator's own bell detector, not certified**) upgraded by `observed_starts` where joinable (**only 2 certified joins in the era** — the collector shipped 07-06; the certified column will thicken nightly). Universe = truth-start events the bot ENGAGED (any buy placement). Latch = first `match_live_detected`. Fills = `entry_filled`; `source=reconcile_adoption` → ADOPTED class (flagged out). Leak $ = settled-attributed (per-share pnl × fill qty; unsettled = 0).

## (a) GUN COVERAGE per cat

| cat | engaged w/ truth start | latched | **detection %** | lag min p10/p25/**p50**/p75/p90 | latch-SILENT |
|---|---|---|---|---|---|
| ITF_W | 122 | 21 | **17.2** | 9.2 / 12.9 / **45.6** / 63.0 / 78.6 | 101 |
| ITF_M | 135 | 36 | **26.7** | 0.4 / 7.8 / **44.0** / 71.1 / 122.3 | 99 |
| ATP_CHALL | 82 | 51 | **62.2** | −5.2 / 4.5 / **30.6** / 53.9 / 75.7 | 31 |
| WTA_CHALL | 20 | 11 | **55.0** | 4.6 / 5.2 / **33.2** / 45.5 / 47.2 | 9 |
| WTA_MAIN | 2 | 2 | 100 (n=2) | ~15–32 | 0 |
| ATP_MAIN | 0 | — | no read | — | — |

**The blind class, sized: ITF is latch-silent on 73–83% of engaged matches, and when the latch does fire it is a median ~44–46 minutes late.** CHALL halves the silence (38–45%) and still runs ~31–33 min late at the median. Only ~10% of ATP_CHALL latches beat the bell (p10 −5.2). Caveat: graded against tape-derived bells (the detector that feeds LATCH-CAL) — the TRUE silent rate can only be worse, since matches invisible to the corpus detector are invisible here too.

## (b) FILL BOUNDARY (live-booked fills; ADOPTED flagged out)

| cat | pre-gun | grace | **post-grace n** | **post-grace leak $** | post-grace paths (silent / latch-late / in-latch-grace / outlived-latch) |
|---|---|---|---|---|---|
| ITF_M | 82 | 5 | **19** | **−4.95** | 12 / 6 / 0 / 1 |
| ITF_W | 82 | 6 | **13** | **−1.57** | 7 / 1 / 2 / 3 |
| ATP_CHALL | 29 | 3 | **18** | **−9.35** | 5 / 6 / 3 / 4 |
| WTA_CHALL | 5 | 3 | **1** | **−3.15** | 0 / 0 / 0 / 1 |
| ATP_MAIN | 0 | 0 | **4** | **0.00** | 0 / 2 / 0 / 2 |
| WTA_MAIN | 1 | 0 | 0 | — | — |

- **Post-grace total: 55 fills, −$19.02 settled-attributed.** Dominant paths: LATCH-SILENT 24 fills, latch-fired-too-late 15 (fill landed post-grace but before the late latch), OUTLIVED-LATCH 11 (bid survived a fired latch — MONCOU +110 min, LIXSUN +109 min the exhibits), inside-latch-grace 5.
- **ADOPTED (dead-bot/orphan booking, flagged out): 758 fills, −$167.04** — the 07-08 blackout + restart-orphan class; fill times unreliable, boundary unreadable. This is the dossier's mechanical class, not a gun defect, but note it dwarfs the live-path leak ~9×.
- NO-TRUTH-START: 75 live fills ungradeable (−$22.59) — the coverage debt, not a verdict.

## (c) CANCEL LATENCY at the latch
- Latch → resting-cancel latency (n=87): **p50 340s ≈ grace 300s + ~40s sweep cadence — the graced path works as designed**; p10 48s (ungraced); **p90 5,172s — an 86-minute tail** that needs a name in the next pass.
- **cancel_fill_race: 14 occurrences, ALL label `v4_move_repost`** — every race in the era is the WALK path (cancel refused, bid already fully filled at 5 shares), ZERO latch-cancel races. The race class lives in the walk, not the gun.
- **80 buy placements landed >5 min AFTER a fired latch on the same event** (LEHZVE +68 min, MONCOU +21 min, TANVIS +39 min…) — the re-place-after-latch path is real and unsized-by-$ here; includes in-play completion policy, named not convicted.

## (d) EKSLUX — the named test case (W50 Columbus, Ekstrand/Lu, 07-08; all four controls failed, +$1.00 by luck)
True start ~3:50 pm (operator-observed; tape divergence 3:54; **exchange truth: EKS buy filled 3:50:35 pm, maker**). The bot's clock: `kalshi_schedule_primary` said **7:00 pm** (lied LONG by ~3h10m); `honest_start` NULL all day (pm-honest matcher miss) — every tts read ~+189 min at the actual bell.
1. **Fill timeline vs true start:** EKS @45 rested from 3:00:34 pm, **filled 3:50:35 pm = T+35 seconds, at the gun**; LUX @51 rested from 3:07:06 pm, **filled 4:00:05 pm = T+10 min, POST-GRACE, maker**. Exits: EKS sold @54 at 4:00:56 pm (+$0.45), LUX @62 at 4:08:49 pm (+$0.55) — both cashed in-play, W2.
2. **Conception rule & geometry:** both legs were **independently priced joins** (`v4_place`: EKS dog @45 engagement_join; LUX fav @51 = join at bid_ex_self, last_traded anchor; combined 96 emergent, not cap-arithmetic) — **this pair PASSES price provenance and FAILS the input read: tts input was fiction (239/233 min "to start"), flow state didn't exist as an input.** After EKS filled, LUX rode its original 51 (no reaim in the stream); completion arithmetic never engaged.
3. **Grace enforcement: none existed.** Grace arms on the latch; the latch fired **4:17:21 pm — 27 minutes after the true start** (gun_thin_shadow at 3:50:53: burst 5, would-fire FALSE — the thin-book blind class live). The in-play window 3:50→4:17 ran with resting bids uncancelled; LUX filled inside it. Bonus: the ~3:20 pm deploy restart made both bids **manual-class orphans** first (`manual_bid_observed` 3:20:47; fills booked `reconcile_adoption`, attribution=manual) — ORPHAN CLASS and LYING-CLOCK compounding in one exhibit.
4. **Window stamps:** `scalp_filled` recorded both exits at **"hours_before_commence 2.98 / 2.85"** — two in-play knife scalps ledgered as W1 premarket cashes. Under the S/A ledger this pair would masquerade as a both-legs-filled-both-cashed "W1" lifecycle at 96. FV-at-burst: EKS entry 45 vs FV 32 (**+13 paid above value at the gun**); LUX 51 vs 66.5 (−15.5). Outcome +$1.00: LUCK-POLLUTED n=1, not claimed.

## (e) VERDICT per cat — is the gun trustworthy near the bell?

| cat | detection | median lag | post-grace leak (era) | read |
|---|---|---|---|---|
| ITF_W | 17% | +46 min | −$1.57 / 13 fills | **NO** — the gun barely exists |
| ITF_M | 27% | +44 min | −$4.95 / 19 | **NO** |
| ATP_CHALL | 62% | +31 min | −$9.35 / 18 | **NO for bell-proximate entries; usable as a lagging confirm** |
| WTA_CHALL | 55% | +33 min | −$3.15 / 1 | same as ATP_CHALL, thin n |
| mains | n≤2 | +15–32 when fired | $0 / 4 | no read |

**The number that matters for the T-20m question: the S-line habitat (T-20m→bell) is entirely inside the latch's median blind spot in every cat.** A bell-proximate entry program cannot be graced by this gun as-is; the dossier's "achievable floor lives inside the latch-vs-bell gap" now has its per-cat detection/lag numbers. The $-leak on live paths is small (−$19 era) because post-grace bids mostly just sit; the risk is the EKSLUX shape — unprotected in-play exposure — not realized bleed. Findings only; the fixes (bell recovery, flow-keyed grace) are queue items, not tonight's builds.
