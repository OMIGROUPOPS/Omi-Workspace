# OUTCOME PROOF (C46, two-lane) — C-FUSED-GUN + C-ORPHAN-FINGERPRINT

**Candidate SHA: `ac0c0ffe`** (fingerprint re-adoption at the boot reconcile + C47 assertions; fused gun: te_scoreboard > schedule_live > tape_latch > price_divergence, buy chokepoint refusal post-gun; gun_scorecard.py tripwire renderer).

## Prior art (C45)
- **C-RETENTION-2 (07-06)** — the collector banks OBSERVED in-play transitions per match (`observed_starts`, set-once, `/live/` page). Live since Tue, **never consumed by the gun** — this build is its first consumer. FOUND DEAD during build recon: last row 07-07 7:20 pm, zero rows today (te_live.py process not running). **The deploy includes its resurrection + a keepalive cron — feed liveness is a build component, stated in the close-out.**
- **POST_GUN_FORENSIC (07-08)** — latch-only detection ITF_W 17% / ITF_M 27% / CHALL 55–62%, med lag 30–46 min; 55 post-grace fills (−$19); **80 buys placed >5 min after a fired latch** (the chokepoint hole this build closes); EKSLUX all-controls-fail exhibit.
- **per_match_clock / C-PM-CLOCK** — the honest matcher's row carries `status` (42 'live' rows in the current schedule.json) — **carried in `_pm_honest` since the staging, UNUSED until now**; it becomes fused source (2).
- **Flow-state gauge (07-08)** — live in the monitor; thresholds provisional; not a gun source yet (ratify on forward tape first — EARLY_CANVAS_PART2 caveat).
- **ORPHAN CLASS headstone (LIVING_VAULT 07-08; BOARD #13)** — restart → own orders read as manual → every loop exempts them. This build is that fix.
- **FERCER / E113** — premarket price-divergence must never cancel a resting bid: the divergence tell fires ONLY past the scheduled start on the best-known clock (tts ≤ 0) and within 6h — the premarket knife-class is structurally excluded.
- **C-LATCH-OVERRIDE / ALCCLA + EKSLUX** — a lying clock costs SPEED, not EXISTENCE. Fused corollary shipped: an external-truth gun (scoreboard/schedule) is exempt from the tape-quiet counter-evidence unlatch — the clock is the lying party.

## LANE 1 — MECHANISM (deterministic, per-game vs the prior slate)

**Orphan fix, replayed against today's own tape (the 3:20 pm restart):**
- The jsonl fingerprint registry at that boot would have contained EKSLUX-EKS `0ccc8e25` (placed 3:00:34 pm) and EKSLUX-LUX `fa28c9fc` (3:07:06 pm) — both were instead `manual_bid_observed` at 3:20:47 pm and their fills booked `reconcile_adoption`/attribution=manual. Under this build the orphan pass re-adopts both as `entry_resting` Positions **before the first conception pass** (reconcile precedes the boot audit precedes routing), and the fills book as bot fills in full lifecycle.
- The 07-08 morning class (11/11 direct-API sweep of manual-class restart orphans) becomes a C47 FAILURE (`fingerprint_in_manual`) instead of an invisible class: halt until the re-adoption heals it — the audit asserts ZERO bot-fingerprinted orders in manual class.
- Fail-soft: no jsonl / no matches → empty fingerprint set → reconcile byte-identical to current behavior.

**Fused gun, replayed against EKSLUX (07-08) — stated honestly:**
- On 07-08 as-lived, sources (1)(2)(4) fire NOTHING for EKSLUX: the te collector was dead (no row), the honest matcher missed the event (`honest_start: null` → no status row), and the divergence tell is premarket-blocked on the lying legacy clock (+189 min at the true bell — correct per FERCER). **The gun's coverage is bounded by its feeds; that is why feed liveness (te_live resurrection + keepalive) ships in the same close-out and why the scorecard names misses nightly.**
- With the feed alive, the architecture bound for a TE-covered match: te poll 60s + gun poll 20s ≈ **≤ ~80s after the scoreboard transition vs the tape latch's +27 min on EKSLUX** — graded live tonight (Part 3a table, pre-registered bar ≥90% of feed-covered matches within ±3 min).
- The 80-buys-after-latch class (POST_GUN_FORENSIC c): every one of those placements hits `gun_buy_refused` at the chokepoint under this build (the gun_state stamp persists for the event's life; grace governs exits only).
- Certified overlap set (the 15 observed_starts rows vs the old latch) renders side-by-side in the close-out table (part 3c).

**In-window behavior of untouched paths:** `fused_gun_enabled=false` → all new paths gated off; the only unconditional additions are the tape-latch `_gun_stamp` (logging + state, after the existing latch decision) and the fingerprint loader (read-only scan). Exits and taker sells untouched. `_is_match_live`'s decision logic is unchanged except the external-truth unlatch exemption (which can only PRESERVE a latch, never create one).

## LANE 2 — SETTLEMENT P&L
$0 claimed. The build is refusal/adoption/detection-only: no price logic, no size logic, no exit logic. Counterfactuals flagged, not claimed: post-gun buys refused may forgo occasional in-play completion fills (the operator's standing doctrine accepts this); earlier cancels forgo post-gun knife fills (the MECHANICAL class, negative on every measured cut).

## Regression watches
`gun_fired`/`gun_source` mix per night (scorecard) · `gun_buy_refused` (should absorb the 80-buys class) · `gun_feed_error`/`gun_feed_ambiguous` (feed health) · `fingerprint_in_manual` + `fingerprint_untracked` (must stay 0 after boot) · `orphan_readopted_fingerprint` count at every restart vs banked snapshot.
