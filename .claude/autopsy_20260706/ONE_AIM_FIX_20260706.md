# THE ONE AIM FIX — FV-frame re-diagnosis + time-axis/bell-bucket build (2026-07-06)

**Operator frame (supersedes the Fix-1/Fix-2 split):** each leg's FV = its price at the bell, from the bucket shapes (similar games' W1 paths); each leg AIMS at a discount to its OWN FV along its own path; **goal−basis is a CAP only, never the target's source. Leg 1's fill price is NOT leg 1's value.**

**Prior art (C45):** TIME_AXIS_PROOF.md (07-05) — the first time-axis build, **verdict DOES-NOT-SHIP, Lane-2 −$20.31 / Lane-1 +2.23¢ worse across 189 legs** — with its own re-run conditions now satisfied: (1) the coupling ("time_aware_aim without per_match_clock is strictly worse than flat" — per_match_clock armed 07-05 23:50, census measured 19–77 min corridors); (2) the anchor debt ("re-derivation should be current-price-anchored on honest-anchored time bins" — this build is); A49 (aim = fillable dip, not FV — preserved: the aim is a DISCOUNT to FV, the dip-informed depth, never FV itself); A50 (dips cluster late); aim_time_axis.py + proof_time_axis.py machinery (reused); census I-1/I-2 + Axis-2 amendment (the joint gauge + role paths); the June-12 grave (bound as filter) — directly implicated in Job 1 below.

---

## JOB 1 — the 3 pulled-sibling cases re-diagnosed in the FV frame (evidence for the operator's ≤2¢-branch ruling; NO code change)

Bell = unambiguous tape onset (DAMHUE 09:55, POPSAN 11:13); BUEPOR has no detectable onset — bell = scheduled 16:00, stated. FV below = the leg's ACTUAL price at the bell (exchange tape); every number is a tape print.

### Case 1 — ATPCHALLENGERMATCH-26JUL06DAMHUE (ATP_CHALL) · **the pure lazy-leg-1 case**
- **Leg-1 HUE (faller): filled 20¢ · own FV (bell) = 12¢ → overpaid +8¢ vs its own value.** Its tape kept falling after our fill (min 10¢).
- **Leg-2 DAM (riser): fillable at 80¢** (sell-flow after the pull; traded min 78) · FV (bell) = 91¢. The bound = 97−20 = **77¢ — 3¢ below the fillable level, and the 3¢ was eaten by leg-1's overpay.**
- At leg-1 = its own FV (12¢): bound = 85¢ ≥ 80¢ fillable → **the pair existed at 12+80 = 92 ≤ 97.**
- `reaim_sibling_lower` pulled DAM at 09:32. Outcome: **DAM WON, the naked HUE LOST** (−$1.00 settled) — the pull converted an achievable 92¢ winner-carrying pair into a naked losing single.

### Case 2 — ATPCHALLENGERMATCH-26JUL06POPSAN (ATP_CHALL) · **NOT lazy on the FV frame — the divot case**
- **Leg-1 SAN (faller): filled 8¢ · own FV (bell) = 12¢ → a genuine −4¢ discount to FV.** But SAN's own path dipped to **4¢** (sell-flow-backed) — the dip-informed level was 4, not 8.
- **Leg-2 POP: never traded below 93¢ pregame** (sell-flow min 93) · FV (bell) = 93¢. Bound = 97−8 = **89¢ < 93¢** → pulled 10:14.
- The ≤97 pair existed ONLY at leg-1's divot: 4+93 = 97. At leg-1's FV-discounted-but-not-divot fill (8¢), no ≤97 pair existed.
- Outcome: **POP WON, naked SAN LOST** (−$0.40). Verdict: leg-1 beat its FV but missed its dip-informed level by +4¢ — **the room is eaten relative to the DIVOT, not FV**; this case is why the aim must be a discount to FV per the dip surfaces, not FV itself (A49 preserved).

### Case 3 — ITFWMATCH-26JUL06BUEPOR (ITF_W, bell=sched, stated) · **mixed: lazy-leg-1 + genuinely rich sibling**
- **Leg-1 POR: filled 5¢ · own FV (bell) = 1¢ → overpaid +4¢.** Path min 1¢.
- **Leg-2 BUE: sell-flow after the pull ≥95¢** (earlier full-pregame traded min 81¢ predates our working window — both numbers stated with their spans). Bound = 92 < 95 → pulled 10:54.
- Even at leg-1 = FV (1–3¢): bound 94–96 vs fillable 95 — marginal at best; **the ≤97 pair here was thin-to-nonexistent in the post-pull window.** The miss that mattered was earlier (the 81–95 zone).
- Outcome: **BUE WON, naked POR LOST** (−$0.25).

### The pattern, for the ruling
In **3 of 3** cases the ≤2¢-branch cancel left a naked single that **LOST** while the pulled sibling **WON** (settled: −$1.65 combined + the forfeited completions). Root cause split: 1 pure lazy-leg-1 (+8¢ vs own FV), 1 divot-miss (FV beaten, dip missed by +4¢), 1 mixed (+4¢ vs FV, sibling rich either way). Open-set note: 3 more reaim-pulls are running (ZEBAND, XUXBER, LINMAR) — same mechanism, unconcluded, excluded by scope. **The evidence supports the frame's claim: the bound was the messenger, not the cause — leg-1 buying above its own value/divot is what put the bound below leg-2's fillable level. The ≤2¢-branch doctrine call is the operator's, with this table.**

---
## JOB 2 — THE ONE FIX: built, replayed, verdict — **DOES NOT SHIP TODAY (Lane-1 fail on this replay; deployment was HELD regardless)**

**What was built (re-runnable, `fv_aim_build2.py` → `/tmp/fv_shapes.json`, `/tmp/fv_replay_*.json`, `/tmp/fv_sweep.json`):** the time-axis/bell-bucket aim layer in the operator's frame — per (cat × 20¢-bucket × 10-min T-minus bin), from 4,462 corpus legs (analysis/trades, pre-JUL06 only — no self-leak; bell = unambiguous tape onset): `FV_hat(p,T) = p + drift-to-bell quantile` (own-FV, current-price-anchored — the 07-05 anchor debt paid), `aim(p,T) = p + remaining-dip quantile`, hard-bounded `aim ≤ FV_hat − 1` (a discount to own FV, always), **goal−basis applied as CAP only** (never the target source). Walk model: the 10-min re-derivation trajectory IS the walk, structurally unable to chase above value (the riser's killer excluded by construction, not by a cap). Replayed on the census's 161 concluded games, pair-coherent, fill = sell-flow print ≤ aim while resting (step-③ convention), bell = onset / latch / honest+category-median corridor.

**The frontier (FV strictness × dip depth — six cells, all ~identical):**
| params | pairs (old 133) | gap med (old 12) | lazy legs (old 88/177) | Lane-2 (old −$23.88 same-basis) |
|---|---|---|---|---|
| fv .5 dip .75 | 56 | 18 | 0 | −$51.50 |
| fv .5 dip .9 | 55 | 16 | 0 | −$61.25 |
| fv .75 dip .75 | 57 | 17 | 0 | −$50.55 |
| fv .75 dip .9 | 50 | 17 | 0 | −$78.95 |
| fv .9 dip .75 | 57 | 17 | 0 | −$50.55 |
| fv .9 dip .9 | 50 | 17 | 0 | −$79.00 |

**Verdict against the three held conditions:** (a) beats the −$20.31 verdict on the new basis — **NOT MET** (Lane-1: participation 50–57 pairs vs 133, joint gap 16–18 vs 12; Lane-2 worse at every cell, n=161 flagged); (b) walk/repost interaction — modeled (structural FV−1 bound; 156–165 sim fills came from later walk steps); (c) walk-cap honest anchor — staged spec stands, moot until (a). **Per the pre-registered discipline this does not arm. No flag, no restart.**

**The two findings that survive the failed replay (both real, both matter):**
1. **The lazy-leg class is enormous and the frame kills it: 88 of 177 scoreable real fills (~50%) filled AT/ABOVE their own FV_hat** — the census's paid-over-joint-best +8.5..+13¢ lives here. The frame eliminates it by construction (0/…) — at the cost below.
2. **The structural tension, quantified: demanding every leg strictly beat its own path-median FV caps per-leg fill probability near 50% and pair participation near ~35% on the same slate.** The real bot's 92% per-leg fill rate and its 88 lazy fills are the same coin, two faces. Any aim-below-own-FV layer TRADES participation for entry quality; the exchange rate on today's data is bad (77 pairs lost for ~4–6¢ better entries on survivors) — **on today's data and today's model.**

**Named model limits (why this replay under-states the fix — measurement debt, not excuses):**
- **Tape-only anchoring:** the sim's "current price" is the last PRINT; on ITF no-trade books (the census's own skip_no_trade class) that anchor is stale-low and the aim sits unreachable — the live bot anchors on the BOOK (book_bid/book_ask in v4_place). A book-anchored replay (premarket_ticks/ws_depthrec data exists) is the correct next instrument.
- **Card-era corpus for honest-era windows:** the 4,462-leg shape corpus predates the flip — its early-T cells (the honest premarket the fix targets) are the thinnest exactly where the aim layer would live. Every honest-clock night now accumulates the missing cells. Same coupling lesson as TIME_AXIS_PROOF (07-05), one level deeper: first the clock had to arm before the table was reachable; now the table's TRAINING DATA has to accumulate under the armed clock.
- **In-match entries out of scope:** 69 of 294 real fills landed after the bell (55 after a true onset) — the sim's W1+corridor scope excludes them by design; they belong to the gun/grace machinery, not the aim layer.

**Disposition:** deployment HELD (operator's order — condition (a) unmet regardless). The frame's Job-1 evidence (lazy-leg-1 root-caused 2 of 3 pulled-sibling naked singles) and the 88-lazy-leg census stand as the motivating record. The build, shapes, replay and frontier are committed and re-runnable; the re-run trigger is honest-era shape accumulation (nightly) + the book-anchored replay. Then Plex, then the rolling slate.

## JOB 3 — standing ledger (unchanged, acknowledged)
Thin-gun (shadow staged, blind class 75% of concluded games per census AX4) · thin-book depth · serialization cost (P2b/P4 placement guards live since 12:15, full serialization design parked behind §4H) · monitor fixes (ZT2 exchange-basis, ZT3 conception-ordering) · MULVILLE cell-58 check parked · master-plan pointer. No action taken from this session.

---
## LEDGER STATE (updated per PLEX_REGRESSION_RULING §5, 2026-07-06)
- **THE AIM FIX: BLOCKED-ON-DATA.** Re-run trigger is COVERAGE, not vibes (AIM_V2_SPEC §3): ≥50% of target cells (Tbin 12–36 × all buckets × ITF_M/ITF_W/ATP_CHALL/WTA_CHALL) at n_honest ≥ 30 → the accumulator re-derives automatically and reports (`SHAPE_RERUN_REPORT_*`). Coverage visible nightly in `data/shape_corpus/coverage.json`.
- **The ≤2¢ branch: RULED 2026-07-06 (OPERATOR_RULING_2C_BRANCH.md) — the a/b menu REJECTED; per-leg conditional patchwork BANNED AS A CLASS** (leg-2's bid is never a function of leg-1's accounting). The cancel branch stays as-is, **status INTERIM-ARCHAIC**, dissolved by the aim build when the coverage trigger fires (the pair priced as one state, both bids from one read — June atomic-pairs + the 90/10 frame, converged). **Interim's known cost, logged: DAMHUE/POPSAN/BUEPOR (−$1.65 settled + forfeits, all three pulled legs won) + ZEBAND / XUXBER / LINMAR live same-mechanism at ruling time.** Constraint on the running jobs: no sibling-level conditionals while they build.
- Machinery landed this cycle: `analysis/shape_accumulator.py` (nightly cron 04:45 ET) · `analysis/aim_v2_harness.py` (walk-forward, built now, runs when coverage permits) · `AIM_V2_SPEC.md` (regression estimator, hard min-n, no-silent-interpolation — discipline also imposed on the median script today: floor 30, explicit borrow counting) · z-score shadow staged in live_v4.py (`aim_zscore_shadow`, default OFF, byte-identical; own gate later).
