# EVENING CUT — 2026-07-08 (SEND-ORDER #6; ET)

## 1. GUN PROOF TABLE (Part 3) — delivered; the ±3-min bar is UNEVALUABLE tonight, stated plainly
**37 gun fires; 17 graded events: 13 FRESH / 4 CATCH-UP** (full table `.claude/gun_scorecard/` convention; tonight's render in the session log). Sources: te_scoreboard 3 (all catch-up, the boot backlog) · tape_latch 10 · price_divergence 4.
- **Feed-covered FRESH fires: 0 — the pre-registered bar (≥90% within ±3 min) cannot pass OR fail tonight.** Two causes, both named: **(a) TE /live/ does not carry the US-evening ITF wave** (6 matches listed at 8:04 pm — the afternoon Asian wave + tour; none of tonight's firing wave) — a COVERAGE bound, not a bug; **(b) the observed_starts bank starved on `database is locked` from ~5:19 pm** — a stuck tennis_odds transaction held the 16GB db's write lock ~3h (queued #19 biting live). **Fixed tonight: tennis_odds bounced (lock released, bank verified working 8:05 pm) + te_live busy_timeout=30s shipped (`226a4d13`).**
- **The fused-gun close-out therefore REMAINS OPEN on Part 3a** — expected to certify on the Euro-morning wave (TE's strong coverage zone, where the afternoon's catch-up fires all came from) via the 6:10 am scorecard cron. Everything else about the gun worked tonight: the wave was caught by the fallback sources exactly as the priority order intends.
- **Blind class (3b), sized honestly:** tonight's 13 FRESH fires are 100% tape/divergence-sourced — the scoreboard was blind on this wave by coverage+lock. Standing exposure rule where NO source fires: unknown-start conception stays blocked (no_reliable_commence_source + horizon), and bell-proximate entries stay blocked-on-gun-certification (the T-20m ruling's evidence bar).
- **(3c) EKSLU replay:** old latch +27 min stands as baseline; fused bound = ≤~80s after TE listing (EKSLUX WAS TE-listed by 5:03 pm; its listing moment is unknowable retroactively — the feed was dead 3:50→5:03). The certified-overlap side-by-side grows nightly with observed_starts.

## 2. LYING-CLOCK REPOST WATCH (7–9 pm) — CLEAN, one supersession
- **JANFUN / BEKPAN / JUHKLO / VANSEL: entered the window clean** — defer count 1 each (the final pre-window tick), 0 refusals, no churn (1–4 routine management cancels); latest steady audit **PASS 0 failures / 0 flags** (conception_beyond_horizon = 0 on the conservative anchors).
- **MILMIS: superseded by a REAL gun fire** — tape latch FRESH 5:41 pm (the "Jul-9 07:00Z" schedule was wrong for it too), grace armed 5:41:34, **completion bid cancelled GRACED 5:46:44** — the C-RIDE-LIVE-OFF grace machinery working exactly as designed on the exact leg the morning's starvation drama was about.

## 3. RETRO-STAMP consumed
EKSLUX's two "W1 scalps" struck to W2/IN-PLAY, mechanical-flagged `lying-clock`, pair excluded from BOUHAR/W1 metrics (`.claude/anchor_20260708/RETRO_STAMP_20260708.md`). Tonight's clean-entry read carries the flags; no other lying-anchor rows graded.

## 4. Book + cash (full mark-to-market reconciliation rides the morning dossier per format law)
Kalshi cash **$829.67** · book at last audit: **28 unsettled positions / 69 resting orders, PASS 0/0** · PM $80.00 external (unchanged). Day context: two gated bot deploys (fused gun+orphan `6d84f27e`, C-ANCHOR `1eeebc7b`), one collector patch, zero error-events post-boot on both.

## 5. New named gaps (queued)
- **#20 GUN-STATE PERSISTENCE:** `_gun_state` is in-memory — a restart forgets fired guns until sources re-fire (MILMIS's post-restart move_repost cancellation at 7:56 pm is the exhibit; the fingerprint lesson, applied to the gun). Catch-up class covers live matches within a poll cycle; persistence closes it properly.
- **#19 amended:** bit live tonight (the 3h bank starvation); busy_timeout shipped; WAL conversion remains the real fix.
