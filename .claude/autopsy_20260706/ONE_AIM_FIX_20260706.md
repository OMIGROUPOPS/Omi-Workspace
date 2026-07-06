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
