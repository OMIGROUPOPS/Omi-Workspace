# OUTCOME PROOF (C46, two-lane) — C-REALITY-BELL (fallback bell + reality invariant + aim sentinel + unlock conception; nothing else rides)

**Candidate SHA: `SHA_RB`** (live_v4.py: gun source 5 + bell-coverage + reality check + sentinel fix + conception/in-play stamps; config keys; monitor parses + MORNING REVIEW feeds; scorecard BELLS-MISSING footer).

## Prior art (C45)
- **The operator's failed test (vault, verbatim, recorded first)** — SAIDEL: entry 62, market 24, bought in-play, graded premarket, hand-cancelled in set 2; the FV sweep compared the model's two FVs to each other, no market comparison existed anywhere.
- **C-FUSED-GUN** — sources 1–4 and the stamp machinery this bell rides (grace, buy refusal, cancels, persistence, scorecard grading); the bell is source 5, LAST, the gun stays primary.
- **FERCER (06-19) + volume-burst prematurity (+22 min median)** — why the bell is NOT a bare volume trigger: rate + (start OR rise) — premarket dips FALL, they do not rise on sustained tape.
- **Match-start signal finding (06-19)** — "no reliable match-start" — SAIDEL adds the fourth blind spot (clock lied EARLY, TE coverage hole, no burst, divergence clock-gated); the bell is the bot's own bell.
- **C-BAND-CLAMP (ADAIMA@1 class)** — the chokepoint refuses <5¢ placements; the sentinel fix moves the refusal to the AIM so a 1¢ target is never even proposed (make-it-stick, at the source).
- **EXHIBIT1/FV_SWEEP (this morning)** — the co-faulted sweep; the reality invariant replaces model-vs-model with book-vs-MARKET.

## LANE 1 — MECHANISM (both replays on today's tape, offline)
- **A (bell):** SAIDEL replay under deployed constants (rate ≥0.4/min trailing 10 min; rise ≥4¢ vs window-open ref when no clock has started; sustain 1 poll): **bell fires 11:46:40 AM (prints10m=10 → 1.0/min, rise +4) — the 11:47:08 Dellien buy is REFUSED with 28 s margin** (chokepoint gun_buy_refused on the stamped event). Constants honest: prints never exceeded 63 (rise +4, not +5) and the pre-buy window was 29 s — disp=4/sustain=1 are what the tape supports; every fallback fire is graded nightly by the scorecard vs tape onset, so premature-fire drift is self-auditing.
- **B (reality):** Dellien basis 62 vs market mid 23.5 at 12:30 PM → divergence 38.5 > 25 → `reality_divergence` FLAGS (and by 1:00 PM the mid returned to 59.5 — the invariant flags the divergence window itself, exactly when a human should look).
- **Sentinel root, one line:** `_reshuffle_leg2_target` returned `max(1, min(aim_level, goal_level))` — goal_level ≤0 (leg1_basis ≥ goal) or a collapsed faller anchor became a 1¢ "aim". Now None → `aim_unresolved_refused` named; twin `max(1, ...)` in the ≥50 branch fixed identically.
- **Conception:** `conception_stamp` at unlock-qualification per leg; monitor grades early buys against it (earliest stamp wins).
- **Byte-safety:** bell behind `fallback_bell_enabled` config; no order-path change beyond the refusals the gun machinery already owns; reality check is log-only; sentinel can only REMOVE placements (degenerate ones).

## LANE 2 — SETTLEMENT P&L
$0 claimed. The bell prevents in-play buys; the invariant renders divergence; neither prices anything.

## Regression watches
fallback_bell fires/night + their scorecard grades (premature = FERCER regression signal → tune constants) · `bell_missing` stays 0 (any = an uncovered live match, zero-tolerance) · `reality_divergence` reviewed each AM · `aim_unresolved_refused` counted (each = a named degenerate level) · `pre_conception_buy` ungradeable lines must stop appearing · leg2_reshuffle_reaim to targets <5 must never appear again.
