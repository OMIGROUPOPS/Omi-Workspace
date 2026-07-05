# PRIOR-ART INDEX — topic → lesson codes / docs (the gate's one-lookup entry point)

Serves `.claude/rulings/PRIOR_ART_GATE.md` (C45). Grep here FIRST; then open the cited source and quote the
verbatim line. Sources: `arb-executor/docs/LESSONS.md` (this branch; codes ≥C39/F39 live here),
`JUNE_VAULT.md` + `JUNE_VAULT_APPENDIX.md` (canonical on **blend/agent-derivation** — full verbatim lesson
corpus A1–G24 lives in the APPENDIX), `arb-executor/docs/ROADMAP.md` (T-items), `.claude/rulings/`,
and the **gated-flags inventory** (`grep "self.config.get(" arb-executor/live_v4.py` — staged-but-never-armed
builds ARE prior art). Living doc: extend it when a grep finds something this index missed.

## Clocks / schedules / match-start
- **T51 (ROADMAP:211, 2026-06-01)** — Kalshi start fields are "frozen coarse placeholders"; LESSONS §6 adds "uniform noon-UTC". `T51_HARDENING_SPEC.md:8` — T-15 buffer fires at the wrong wall-clock off a locked-on-first placeholder.
- **C32** — expected_expiration_ts > settlement_ts, 100% of probe (early-settle is canonical). **C19** — Kalshi lifecycle timestamps ≠ match reality. **A35** — volume/min is the cleanest match-start anchor. **A25** — live_scores has no in-match state. **F16** — timezones are not uniform (ET/UTC/CET). **F35 + T37-RECAL** — PMU match-start hierarchy fails a recoverable ~6.4% cohort.
- **Vault 4I / CLOCK_AUDIT.md (2026-07-05)** — card-marker verdict quantified (+1.8h CHALL / +4.1–4.4h ITF / mains negative); gun certified vs TE/ESPN (invalid on _MAIN); **ITF has no premarket**. **Vault §0B** — MEASURE-BEFORE-READ half-fix chain (Gen1–4 → Part 1).
- Builds: C-SCHEDULE-TRUST-FIX (set-once start corrections); **C-KALSHI-OCC (`kalshi_occurrence_fallback`, STAGED-NEVER-ARMED)**; `kalshi_schedule_primary` (armed Jul 2 — the Gen-3 regression); **C-PM-CLOCK Part 1 (`per_match_clock`/`_shadow`, STAGED ce38ca8c)** + PART1_SPEC.md (schema freeze, staleness fallback). Match-start-signal forensic 2026-06-19 (schedule.json `status` unread; burst median +22min premature).

## Caps / bounds / ceilings
- **C-BOUND-RULING (Vault 4I, DEPLOYED 21eaad4, 2026-07-05)** — THE law: resting/reprice/completion ≤97 combined on every branch; complete_cross ≤100 + legs 5-95¢; 99-ceiling DEAD; tripwire on goal-breach. `tests/test_bound_ruling.py` = the bars.
- **T50 (Vault §1)** — `_paired_basis_ok` WORKING, do not rebuild; over-par ~0% live. **C42** — re-aim on ANY sibling basis arrival, no price-bucket exemption. **paired_cap = BANNED lineage** (C-CAP-REMOVAL residue struck 3×; C-FALLBACK-BOUND 733341f closed site 2). **A49** — T-20m anchor is the sucker's baseline (dip ≥1¢ on 97%). **B13** — threshold metrics on bounded variables produce ceiling artifacts. Aim-table Item5: ceiling is COMPLEMENTARY to reshuffle (pays favorite UP; reshuffle only lowers).

## Repost / walk / chase
- **Aim dispatch (5b924f10/ba08243, 2026-07-03)** — STATIC +1.89¢ FV vs CHASED −1.22¢ (Item 4 census); ALCCLA +26¢ premarket walk; fixes: `premarket_walk_cap` (MAIN2/CHALL3/ITF4, ARMED), `reach_repost_cap` (gated). **A49/A50** — aim = the dip, not FV; dips heaviest late-window. **C44 amendment** — riser fills are adverse selection (8/11 above burst-FV); depth buys cents, not selection.
- C-CHURN-FIX (`repost_hold_same_price`, pin-exempt); walk-truncation fix a16d438; staircase walking (`_staircase_bid`, 4-cat abort bars); join-the-bid trial = starved behind MM walls (night-1 diag); wall-starvation obs e6a76c4 (dip-through clears the queue — necessary-not-sufficient). **A51** — hot-swapped tables don't update open positions. **B25** — minute-cadence sims undercount threshold-cross fire rates.

## Gun / latch / grace / liveness
- **T51 (ROADMAP:211)** — the rebuild mandate (volume-acceleration + reliable status source). **INVARIANT 2 (live_v4 CUT_GUN block)** — cut-gun and cancel-gun constants are DELIBERATELY separate; never merge.
- C-FEEDER FIX-1 — TTS floor + two-stage latch + counter-evidence unlatch. **E113** — premarket movement gate (FERCER; fail-open on no-ref). `sustained_flow_latch` (K=3). **`latch_tape_override`** — a lying clock costs latch SPEED, never EXISTENCE (ALCCLA: TTS floor blinded by kalshi_schedule_primary). `match_live_grace_kill` (gun+300s hold-then-cut; freeze_at_gun SHELVED as contradicting it). C-RIDE-LIVE-OFF (cancel decoupled from ride_live).
- Vault §6 — the gun-cancel defect (premature cancels, double-edged: half protected / half missed; median +22min early). **CLOCK_AUDIT** — gun INVALID on _MAIN (premarket volume trips the fixed bar). **C-SCALE-GUN (`scale_gun_shadow`, STAGED ce38ca8c)** — scale-aware bar, observe-only. SHINIS forensic — the full latch/cancel/fallback timeline on one leg.
- **Tape supremacy (Plex, re-anchor ruling)** — NO clock touches liveness/abandon; grep-proof required at every diff.

## Pair governance / completion
- **PRIORITY 1 = PAIR (Vault 0A, verbatim)** — rest bids on BOTH legs always; the cap binds the SECOND leg's walk, never participation. **Vault 4E** — the completion-gap cancer (blind-laying → keep loser, strand winner). **Vault 4G** — stranded-winner recovery measured; ALWAYS-LAY-BOTH neutral not +EV (β gun-cross NO-SHIP).
- **C43** — fill-is-information (WATSHI); one leg filling forces reassessment of the other (0A thesis). **C42** — re-aim on sibling arrival. `leg2_reshuffle` (goal 97, ARMED) — sequenced re-aim, NOT a cap. `rest_both_legs`; `repost_sibling_on_boot`; WTA_MAIN abort half-arm lesson (cat-abort → naked singles via fallback); `pair_governor_scoot` DISARMED (duplicate-buy). Single-leg synthesis 2026-06-19 — "one fill per pair" NOT structural; differentiator = per-leg sell-flow. **E18/B23** — the bilateral-capture frame. **A2** — never report pair-completion % as one number.

## Exits — OUT OF SCOPE (standing order)
- **⛔ Vault 0A (2026-07-02, verbatim):** exits are SOLVED/VALIDATED (14k-N foundation, conservative taker-scored); "exit looks negative on live trades" = broken-entries symptom; the RECURRING FALLBACK tell = any sentence proposing to change/score/re-target exit policy while ≥98 fills and strands persist → STOP, cite the order.
- **E32** (pre-live date caveat: backtest convention, not a live prohibition) + **A43 OVERTURN** (live monotonic cut +$205/wk — pre-June lessons never veto live results; check every lesson's DATE). Sealed surface = `exit_surface_gated_optima/LOCKED_DOWN.md`. C-MONOTONIC-CUT gated OFF (b1aaef9, shadow-first). FUCKUP-3 (exit-harvest: band sells winner, holds loser). **A46 RETIRED**, A47 (+1¢ never conservative), A9 (scalp-achievable constraint).

## Sizing
- **E20** — per-cell treatment, no global config. **G22** — N is the market, ct is the size; never conflate. Baby sizing 10/5 (2026-04-10, entry_contracts in deploy config). **B23** — sizing interacts with bilateral capture via queue/fill mechanics; volume is a primary partition axis (A31).

## Meta / method (cite these in any prior-art section)
- **C40** — LAW: no deploy without lint + smoke (deploy/lint_gate.py + smoke_replay.py; born of C39's duplicate-def kill). **C45** — LAW: the prior-art gate (this index serves it). **C44** — the causal audit method (EARNED/GIFT). **F39** — exchange truth only for result-side. **D15/D16/D18-class** — read disk before concluding (Vault §0). **G24/A32** — operator pushback is signal. **A33** — no apology loops. Vault 0A OPERATIONAL INVARIANTS 1–5 (tier-partitioned reporting; boundary contamination; ceiling results outrank caveats; peak ≠ scope; closure over deferral).
