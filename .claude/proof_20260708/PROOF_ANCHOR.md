# OUTCOME PROOF (C46, two-lane) — C-ANCHOR: the lying-clock fix (board #14)

**Candidate SHA: `1eeebc7b`** (anchor hierarchy + datemiss_36h matcher recovery + clock_liar detector + conservative horizon + anchored window stamps; `anchor_hierarchy_enabled=true`).

## Prior art (C45)
- **per_match_clock lineage (C-PM-CLOCK → flip Ratification #20, 07-06)** — the honest clock exists; its MISS class (honest_start null) left kalshi lying alone. This build closes the miss class, not the clock.
- **C-CONCEPTION-HORIZON vault amendments (both, 07-08)** — "the bound is only as good as its anchor and it says so": GILOBR (lied SHORT — horizon counting down to a knife) and the evening census (5 sibling-repost completions re-placed beyond T-8h through a blind chokepoint refusal, deliberately not re-swept: sweeping without fixing the anchor is churn). This is the fix that ends the churn argument.
- **#11 kalshi_schedule_primary coexistence + the staged C-KALSHI-OCC lane** — the 36h acceptance bound reuses the C-KALSHI-OCC real-future-≤36h guard number; kalshi occ stays the LAST anchor, never alone when TE coverage exists.
- **Fused-gun sources (07-08)** — the scoreboard feed now provides a truth signal the matcher can use: `gun_truth` heads the hierarchy; SNIAND's proof map (both clocks lying by 574–934 min, gun right) is the live exhibit.
- **EKSLUX (POST_GUN_FORENSIC d)** — lied LONG: 7:00 pm claimed vs true 3:50 pm; two in-play knife scalps ledgered "~2.9h before commence". The anchored scalp stamp exists because of this row.

## LANE 1 — MECHANISM (deterministic, replayed against today's own tape)
**The five reposts (VANSEL/JANFUN/BEKPAN/JUHKLO/MILMIS, ticker 26JUL08, true starts Jul-9 07:00–09:00Z):**
- As-lived: `_date_ok` rejected their true Jul-9 schedule rows (Δ ≈ 16h > 12h) → `honest_start: null` → kalshi date-coarse said in-play/past → the horizon chokepoint read "no violation" and the sibling-repost path re-placed them beyond T-8h invisibly (evening census: in-code flag 0, direct census 5).
- Under this build: the matcher returns the Jul-9 row as `datemiss_36h` (Δ 16h ≤ 36h) → `clock_liar` fires (kalshi vs te ≥ 60 min) → `_horizon_state` takes the CONSERVATIVE (nearer = kalshi) side → the held-leg completions stay legal and RESTING (no sweep-churn, no re-starvation — the operator's own no-sweep ruling, now principled), while the audit sees the liar flag instead of a blind 0.
**EKSLUX:** the gun fired 4:17 pm (tape latch, late) — under this build `anchor_source=gun_truth` classifies both exits as NOT-scalps (fired gun = never a scalp) and any surviving pregame stamp carries `anchor_source`/`clock_liar` — the fake-W1 lifecycle cannot grade blind. With the (now-live) TE feed the gun fires minutes from the true 3:50 pm, and the anchor follows it.
**Byte-identity:** `anchor_hierarchy_enabled=false` → `_horizon_state` and the scalp classifier take their exact prior paths; the matcher's datemiss return only occurs where BOTH clean passes already failed (the previous outcome was None — strictly additive coverage on the miss class); `_pm_honest` gains a key no existing reader consumes when the flag is off.
**Blast radius stated:** the datemiss row also reaches the real resolver where `_match_event_pure` feeds it — on lying-ticker events the legacy clock improves toward truth (this is the intent: kalshi LAST, never alone); wrong-instance risk bounded by the 36h guard + the liar flag + conservative gates.

## LANE 2 — SETTLEMENT P&L
$0 claimed. Anchor/classification/refusal logic only; no price, size, or exit-band logic touched.

## Regression watches
`clock_liar` count/night (the class size, finally measurable) · `schedule_match{method:datemiss_36h}` · `conception_beyond_horizon` (now conservative-anchored — must stay 0 on true clocks) · scalp_filled rows with `clock_liar:true` (should be rare and never blind) · the five reposts' matches re-anchoring at the next resolve cadence.
