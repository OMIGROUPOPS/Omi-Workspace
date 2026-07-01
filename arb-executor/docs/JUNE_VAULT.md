# THE JUNE VAULT — OMQS ground truth, read FIRST every session

**Purpose:** Stop re-deriving what's already settled. Every fact here is verified from disk/REST, not memory. If you're about to conclude something, check here first — odds are it's already concluded, tested, or dead. Shared reference for Fable, Plex, and CC.

**Last verified:** 2026-06-30 against HEAD `d2ac207` (blend/agent-derivation) + the Jun-30 live dump.

---

## 0. THE RECURRING FAILURE MODE (read this about yourself first)

The 30-day loop: reach "understanding" → declare it → don't follow through → next session re-derive the same thing as if new. In one session alone, six "root causes" were each killed by data: over-par, entry-timing, completion-dead, catch-the-firmer, fill-sequencing, locked-arb. Every one felt like a discovery. Every one was already on disk or refuted by the records.

Disciplines that must hold:
- Read disk/cross-reference BEFORE typing a conclusion or a prompt (D18/D15/D16).
- **A lesson's DATE matters — pre-June findings are CONTEXT, never a VETO on a live-validated result.** Pre-live findings (May and earlier: A43, E32, the sealed exit surface, Path B/C) cannot be the final word on live behavior, and must NEVER be used to pre-rule the outcome of a live measurement. **PROOF this session: A43 (May 23) said "remaining headroom is exit-side, entry conditioning doesn't pay" and was cited all session as if it settled what's possible — then the LIVE tape (Task B) found a positive exit-side rule (+$205/week monotonic cut) that A43's offline corpus could not have surfaced (it had no mechanism to model a mid-match stop).** The live tape overturned the pre-live framing. So: when a live measurement (e.g. the peak-then-reverse sweep) returns a result, judge it on the live tape alone. A43's "exit conditioning doesn't pay" was offline + pre-live and CANNOT veto a live-validated exit/band change. The sealed exit surface is the CURRENT DEPLOYED config, NOT a proof that no better exit exists. Check every lesson's date before citing it as law, and if it predates June, it is an input to be tested, not a wall.
- One step at a time. Loop: CC responds → Fable reads → kick to Plex → Plex responds → kick to CC. Each turn does ONE thing.
- Plex can only read what's put in front of it (it can't see CC's raw output or Fable's context). Ground-truth artifacts go to Plex via the public repo raw URL.
- Operator pushback is signal, always right (G24/A32). Investigate, don't defend.
- Authoritative source = Kalshi REST + enriched live book. NOT the per-minute historic candle (too coarse). NOT the WS recorder (unreliable). NOT CC's prose summary (garbles — trust discrete facts: hashes, timestamps, counts).

---

## 1. WHAT'S SETTLED — DO NOT RE-OPEN

### Entry method: SOLVED and DEPLOYED.
- Path B v4 (T47, commit c90985b, 2026-05-23): net-PnL-optimal offsets are SHALLOW (1-3¢ on 27/36 cells). Deep-discount chasing is DEAD — the fixed +band exit means a deeper entry adds no exit upside, only raises miss rate.
- Deployed: entry_table_path = docs/policy/per_regime_offsets_v2.csv + entry_table_cell_path = docs/policy/entry_table_percell_conservative.csv. The bot runs this NOW.
- **A43 (2026-05-23, PRE-LIVE — date caveat, PARTIALLY OVERTURNED LIVE):** per-event entry-side conditioning (fv discount/distortion gating, offset modulation, execution-mode switching) was TESTED offline (Path C, fv-predictor AUC 0.73, real signal) and CANNOT lift ROI through the fixed +band exit. Phase 2 +0.08pp (noise), Phase 3 −0.24pp (negative). Corollary it stated: "remaining headroom is exit-side, not entry-side." **⚠️ OVERTURN (Jun 30 live, Task B): A43's offline corpus had NO mechanism to model a mid-match stop, so it could not see the live exit-side rule that the tape found — the monotonic in-match cut, +$205/week, both gates passed. A43's "exit conditioning doesn't pay" is REFUTED for the live mid-match-cut channel. Do NOT cite A43 to veto a live-validated exit/band change.** The entry-side distortion-gate part of A43 (gating on fv) DOES still hold live — Task A confirmed the gate is unbuildable because the distortion signal is forward-only (we fill on dips, entry > premarket-FV+X fires on nothing). So: A43 entry-side = confirmed live; A43 "exit-side is the only headroom AND it's just static-offset re-opt" = overturned, there's a live mid-match-cut lever it couldn't see.
- fv_burst instrumentation is observe-only BY DESIGN (A43 proved gating on it doesn't pay) — not an oversight to "wire up."

### Exit: sealed, validated.
- exit_table_dir = data/durable/exit_surface_gated_optima/ (LOCKED_DOWN.md, May). Per-cell net-PnL-optimal band, one row per 1¢ cell. Exit = min(fill + band_x, cap), posted ONCE at fill, static.
- E32 (2026-05-14, PRE-LIVE — date caveat): no-stop, ride to settlement. BUT this is the BACKTEST scoring convention (settlement is the answer key — no mechanism to model a mid-match stop offline). It does NOT by itself prohibit a live stop.
- Flatten-vs-ride WAS tested live: the June-2 $6.15 RUN-2 counterfactual showed blanket early-flatten FORFEITS in-play bounce. A naive stop-loss is not free — it forfeits recoverers. Whether a SELECTIVE downside cut nets positive is the one open tick-tape question (§4).

### T50 (paired-basis over-par guard): WORKING. Do not re-build.
- _paired_basis_ok confirmed working June 3: 1,440 skips, combined ∈[100,103], ZERO false-blocks at ≤99, prevented 2nd leg on 60 over-cap pairs.
- Over-par is ~0% live (1 leg in 591 since Jun 26). The completion-ceiling built Jun 30 was solving a near-dead problem.

### Mechanism truths (do not re-confuse):
- There are NO arb "boxes." Kalshi books a sell-yes band-exit as a sell-no fill. Every position is a single directional YES bet with a band-exit posted. Two players both getting YES = incidental co-capture of two independent single-leg dip-captures.
- NEVER use "locked arb" / hold-to-settlement. Settlement is structural bleed; strategy is in-match volatility capture before settlement.
- entry_mode is unreliable (mislabels ~50% of fills). Read play_type + exchange is_taker from /fills.

---

## 2. THE LIVE STATE (HEAD d2ac207, 2026-06-30)

Flags ON: staircase_hold_at_bid, depth_aware_join (floor 50), bestbid_follow_at_touch (gap 15), liquid_repost_at_touch, match_live_grace_kill, sustained_flow_latch (K=3), itf_entry_borrow, completion_combined_ceiling, completion_all_cells.
Flags OFF: pair_governor_scoot (disarmed Jun 29 23:24, duplicate-buy), fv_anchor_placement (disarmed Jun 25), paired_cap_enforced.

The 4 bisect flags (Plex's roll-back-and-bisect target):
- pair_governor_scoot: armed Jun 26 03:44, NOW OFF (disarmed Jun 29 23:24). Was ON during green.
- liquid_repost_at_touch: armed Jun 29 04:31, NOW ON. First Monday change.
- match_live_grace_kill: armed Jun 29 14:55, NOW ON.
- sustained_flow_latch: armed Jun 29 15:59, NOW ON. K=3.

KEY: the GREEN window (Jun 26-28, profitable) ran pair_governor ON + the other three OFF. NOW runs the INVERSE: three Monday flags ON, pair_governor OFF. The bot is running the opposite flag config from the profitable days.

---

## 3. THE 5-DAY DEPLOY LEDGER

The whole Jun 20-30 arc is ONE problem attacked six ways: the one-sided fill. ~40 gated flags, 61 commits, ZERO strategy changes — all execution plumbing.

- Jun 19 (P0): order CREATE v1 endpoint 410'd (fac74b5) — silently failing.
- Jun 20-24 (entry-solving): fv-anchor "premarket graze" fix (0bfd547, 12/13 T-4h legs resting 3-9c BELOW market, flow trading above — bid too deep, never fills; now OFF). complete-all (0db51c4, completion table had 12 cells/ZERO WTA → 252 no-attempts/0 completions). abort-rearm.
- Jun 25 (P0): cancel v1 endpoint ALSO 410'd (4457a45) — every cancel was silently failing before this. abort-carve (0ebf05b, −$76.85/49 one-fill games). staircase-hold (ce75bf8, −$96.55/314 starved-partner games).
- Jun 26 (six-pack, 15 commits): best_bid_aware_repost (53% offset-starve), depth_governor (lone-top leak), vol_gate, pair_governor (4d7980d, "leg-1 fill = reassess sibling," the principle), wall_skip (BUILT NOT ARMED), bestbid_follow. All "stop legs stranding off-best after the bid moves."
- Jun 27: ITF-borrow (thin books added; dead-input bug volume_tracker=PaperApi-only, fixed to _trade_notional).
- Jun 28: ZERO commits (green ran untouched).
- Jun 29: liquid_repost (04:31), grace-kill (14:55), sustained-flow (15:59), pair-governor-REV (17:32 → disarmed 23:24, duplicate-buy collision).
- Jun 30: completion-ceiling (d2ac207).

Recurring bug class (3×): reading a PaperApi-only attribute on the live LiveV3 class. When the same fix recurs, it's a symptom not the cause.

---

## 4. THE BLEED — what the data actually proved (after 6 wrong theories)

Decomposition of the ~146 naked-loss legs since Jun 26:
- 69% (101): BOTH legs filled, one exited, the other rode to 0. FUCKUP-3 / exit-reach asymmetry. NONE of the six patched causes touch this.
- 31% (45): truly one-sided. Dominant cause = queue-starvation (62%, ~28 legs): at the right price but BEHIND the queue on the firmer's wall — trades went through our 5-lot without filling us. Six-pack off-best-rejoin did NOT close this (queue-position, not off-best). Graze (9, shallow) and completion-dead (5) NOT dominant.
- 101/101 settled naked legs LOST.

"Catch the firmer on leg-1 fill" recovers ~2 legs (60% of losses caught BOTH legs). Not the lever.
The bot ALREADY sequences: 82% of pairs fill ≥5min apart, median gap 42.5min. Sequencing does NOT deepen the combined (~99 either way, set by fixed offsets).

The ideal trade (E18/B23 "double-cash"): both legs filled cheap premarket, BOTH hit +band. +109¢/pair. 70.7% bilateral double-cash at +10c WHEN both captured; ~21-23% unconditional (×~30% feasibility). The vision. Rare. Profitable when it works.

THE TWO-TRADE PROOF (Jun 30, same day, same structure, opposite outcome):
- IDEAL TOPRAQ +135¢: Topo (fav) entry 68 → exit 88 (+20), filled. Bought 16¢ UNDER fair (fv_mid 84) = discount. Rose through band.
- BLEED ERHROD −315¢: Rodionov (fav) entry 70 → exit 89 (+19), peaked 84 (5¢ short), reversed, rode to 0. Bought 3.5¢ OVER fair (fv_mid 66.5) = distortion.
- THE TELL: identical through entry and dog-exit. Only difference = did the favorite's price rise THROUGH its exit band before the match turned it. Same band. Topo's reachable (discount → exit near fair); Rodionov's not (distortion → exit only on outright win).

Exit = fill + band, BAKED IN at the fill price. A high/distortion fill bakes in an unreachable exit. The favorite (high-price) leg has little room to 99, so a wide band is unreachable on reversal → rides to 0. Geometry, not a broken exit. The exit IS proven — it cashes every leg that swings to it.

THE ONE OPEN TICK-TAPE QUESTION (not yet answered, needs per-leg price-path tape): of the falling legs that rode to 0 — would a SELECTIVE downside cut net positive (save on monotonic fallers) vs forfeit (wobble-then-reach legs + killed winners)? The E32/$6.15 tradeoff, measured. Positive → build it. Negative → E32 holds, lever is entry-selection. The only analysis not yet done.

---

## 4B. §4 TERMINAL STATE (2026-06-30 session — all three agents converged)

The §4 "selective downside cut" question (open since the Vault was built) is now RESOLVED into three parts. Do NOT re-derive these — they are validated/measured/structurally-proven.

**CUT #1 — monotonic in-match cut: BUILT, SHIPPED GATED, VALIDATED. The lever in flight.**
- Commit b1aaef9 (blend/kalshi-occ-fallback). Source-verified by Fable: purely additive (+121 lines, 0 changed/removed), byte-identical when OFF, 5 unit tests pass.
- Validated: WEEKVALIDATION held-out Jun 24-29, N=30/X=10, +$204.84, POSITIVE EVERY DAY. Both gates passed (week-positive + N-plateau, signal in first 15-30min, decays past 30).
- Catches: one-way knives (legs that fall from the gun WITHOUT ever printing above fill). ~35% of the bleed (−$237/wk of the loser pool). Fires on ~13% of legs (genuinely selective).
- Architecture (load-bearing, both invariants IN-CODE): new `gun_detected_for_cut` (CUT_GUN_BURST=5, CUT_GUN_K=2) SEPARATE from the cancel gun (LIVE_TRADE_BURST=10, sustained_flow_K=3). INVARIANT 1: cancel path untouched. INVARIANT 2 (documented in the CUT_GUN constant block): NEVER consolidate the two gun predicates — a merge re-introduces the M2 −$25 cost. Shadow-first: `monotonic_cut_enabled` (shadow, logs would-fire) → `monotonic_cut_active` (flattens). Both default-OFF.
- ARM SEQUENCE: `monotonic_cut_enabled: true` → restart → 48h shadow → compare monotonic_cut_would_fire to retrospective set → ONLY THEN `monotonic_cut_active: true` → restart. Cut #1 must shadow ALONE — no concurrent exit/cut changes, or attribution is contaminated.

**CUT #2 — peak-then-reverse (ERHROD class): DEAD as a tape-discriminator. STRUCTURAL, not parametric.**
- The −$648/wk, 65%-of-bleed cohort (legs that peak above fill post-gun, then reverse and ride to 0 — the §5 two-trade-proof ERHROD class).
- All three discriminators (trailing-stop, reversal-magnitude, post-peak-monotonic) are dominantly +EV (+$440 to +$591) but FAIL the every-day gate (over-cut wobbly winners on quiet green days, 75-81% fire rate = a POLICY CHANGE not a discriminator).
- Refinement 1 (confirmed-clean post-peak monotonic): FAILS (+$3.5 total). Refinement 2 (+ peak-gain gate): FAILS (+$0.7), even with fire rate in the 20-40% band.
- **THE STRUCTURAL REASON (do not re-sweep — this is why it's un-discriminable): high save XOR selective, irreducibly. To be selective you must wait M minutes to confirm a clean reversal — but ERHROD reversals are FAST (84→0), so by the time the decline confirms the leg is dying, the price is already at the bottom. The discriminating signal is causally DOWNSTREAM of the price action it would predict; faster sampling doesn't pull it earlier in causal time. Contrast cut #1: one-way knives are visible AT THE GUN (no peak masks them), so the flatten lands before the price is gone.**
- (Optional closure measurement, may or may not have been run: velocity-of-decline as an early signal, V ∈ {0.05-0.2}¢/sec over first {60-180}s post-peak. Predicted to fail the same wall.)

**THE 65% RESIDUAL — reframed as EXIT-GEOMETRY, next cycle's problem (NOT another tape-rule):**
- The locus moves from tape-cut to the exit surface. KEY FACT: the current exit surface is **+band ONLY** (Exit = min(fill + band_x, cap), UP-side only — there is NO −band/flatten primitive today).
- **NEXT-CYCLE SEQUENCE (do not start until cut #1's shadow finishes — clean attribution):**
  - **(a) FIRST: recalibrate the per-cell +band against June live data.** The May sealed surface (exit_surface_gated_optima/) is the DEPLOYED config, NOT proof of optimality (per the §0 date-caveat discipline). Six weeks of live tape never re-fit. The optimizer exists — re-run it. Likely finding: high-fill favorite cells (where +band is unreachable on reversal) get a TIGHTER +band, cashing the up-side earlier before reversals take it back. May shrink the residual with NO new primitive.
  - **(b) SECOND, conditional on (a)'s residual: entry-time band-asymmetric −band/flatten** (per-cell flatten_at = fill − Z, Z from per-cell historical peak-then-reverse magnitude — decided AT ENTRY, sidesteps the late-signal problem). Larger build (new primitive, new config). Justified only if (a) doesn't close enough.
- **NEXT-CYCLE TRAP: when the optimizer re-runs, do NOT ship the updated surface immediately as "better May." Cut #1's 48h shadow + activation finishes first. The recalibrated surface must pass its OWN four gates (NET +ve every day, plateau, per-cell delta sanity-checked vs the §5 two-trade proof). No shortcut because the optimizer "looks better."**

---

## 4C. THE COMPLETE JUNE DEPLOY LEDGER (every deploy, what it tried to fix, what it broke)

77 commits June 15–30. This is the FULL record, not a stat. The pattern is not "wrong feature" — it is arm without isolating → break something adjacent → patch the break → arm again, with TWO core P0s (order create + cancel) silently failing for unknown stretches. Do NOT re-quote a single percentage from any one deploy as "the problem" — read the arc.

Jun 15–18 — entry placement rebuild
- fc3876f abort-seal ATP_MAIN staircase guard.
- d72ac2c JOIN-THE-BID: replaced the ask-1/offset entry clamp with join-the-bid. (Major entry-placement change — how the resting bid is priced.)
- 8cc9ff1 per-minute re-join cadence. d1aec84/da9f6ac join-trial queue telemetry + 5328 oscillation fix + serialize-on-restart. 59565d5 armed join_trial 5c degraded.
- 77fd9fa/13bd67c staircase ship-1/2: anchor-1 clamp + abort gates, dormant.

Jun 19 — P0 #1 + bug-chain begins
- a16d438 staircase-walk-truncation (STEP-6 truncated the walk at T-20). 23a78e8 widen staircase to all 4 cats.
- fac74b5 P0: order CREATE was 410'ing — silently failing. Migrated to create-order-v2. Entry infra was broken for an unknown stretch before this.
- 4dab200/4a5d24b fv-burst observe-only instrumentation (motivation: entries land +1.5–4.6c ABOVE fv — the distortion, measured here).
- 192d2eb/0d928f9 E113 premarket movement-gate (suppress flat-premarket false live-bursts, FERCER class). e6a76c4 wall observe-log.

Jun 20 — fixes breaking the next thing
- dbf1809 abort-fix (counted premarket false-triggers as live). c03e010 E147: UnboundLocalError crashing EVERY walk-step (new_regime/new_offset undefined before the staircase branch).

Jun 21–22 — patching the patch
- 5f6b932 engagement-overclaim (GUNMAK +30 overpay class — stale-path legs overpaying). c3fb773/4ca7a2c complete-cross: basis-gated taker cross to complete single-legged pairs at the gun, armed.
- 22f4f57 fixed the UnboundLocalError that c03e010 LEFT TWO LINES DOWN (:6027/:6034). A fix that created the next crash. cfebd42 commit stranded tennis_schedule.py (git≠reality gap).

Jun 24 — abort-rearm + fv-anchor THRASH
- e90a89e/389983f/1729bd7 re-armable staircase abort, armed.
- 0bfd547 fv-anchor: post resting bid AT last-traded fv (clamped ask-1). 00cb8c0 arm → 822c98d DISARM (placement-price premise review) → c611f09 strip clamp + book-sanity → 482bbd4 re-arm. Armed/disarmed/re-armed inside 24h.
- 0db51c4/706cb3c/ea3e6da complete-all (completion for ALL cells/cats — the table had 12 cells / ZERO WTA → 252 no-attempts), armed.

Jun 25 — P0 #2 + more arming
- 4457a45 P0: CANCEL was ALSO 410'ing — every cancel silently failing for an unknown stretch. Migrated to events/orders-v2. (Create was P0#1 on Jun 19; cancel P0#2 here — both core order paths were silently dead at different times.)
- 0ebf05b/60131a4 abort-carve: place the hedge for a held sibling at abort gates, armed.
- 5a24814 fv-anchor FINAL DISARM: "posts above bid, overrides join-the-bid; backtest on broken sched-4h window + drift coin-flip; 0 fires." (Entry-side fv placement is DEAD — see §1.)
- 03c1a60/ce75bf8 staircase-hold: route staircase legs to post-at-bid + HOLD, armed.

Jun 26 — THE SIX-PACK (15 commits one night, the green config, arm-spree)
- 9760b13/2916d23 event-cat-override (DAEVAS). 3de4fc4/1561e98 best-bid-aware repost armed. 2a5caed/fdf0ae0 depth-governor (depth-aware join, floor 50) armed. fa324d4/a25a9d3 vol-gate (staircase trail-vs-hold by live vol, burst 5) armed. 4d7980d/7a3ab33 pair-governor (scoot fader sibling down on firming leg-1 fill) armed. 2d98bfc wall-skip (BUILT, NOT armed). 6ee8bc9/4e914ee bestbid-follow (small-gap upward follow joins at touch, gap 15) armed.
- 5 flags armed in one night with no measurement gap between them. This is the profitable "green" config — but green = this whole stack at once, un-isolated.

Jun 27 — ITF, dead-input bug shipped LIVE
- f9b8640/6750728 ITF-borrow armed → ddda89a DISARM (volume_tracker is PaperApi-only — live reference ERRORED) → 328ea0a/613b9f7 fix to live _trade_notional → 4eee091 re-arm. Shipped a live ref-error, caught it, patched, re-armed — same night. Same PaperApi-only-attribute bug class that also hit pair-governor (last_trade_price_at_post).

Jun 28 — ZERO commits (green ran untouched — the one measured window).

Jun 29 — THE FOUR MONDAY FLAGS (arm-spree again → duplicate-buy)
- 7c7e058/e95bfb0 liquid-repost (suppress repost roll-down behind phantom walls) armed 04:31.
- b308084/36d9344 grace-kill (5-min grace before match_live cancel on held-sibling pairs) armed 14:55.
- 1660b36/3473a5d sustained-flow (tape-anchored cancel latch, K=3) armed 15:59. 617ab98 obs-log.
- f998231 pair-governor-rev (make the divot-catcher actually fire — live-tape inputs + every-fill) armed 17:32 → f4a766d DISARM 23:24: duplicate-buy collision LIVE (SUMTAK-TAK). Root = completion_reprice + v4_move_repost, INDEPENDENT of liquid-repost; serialization fix (one-post-per-leg-per-tick) NEVER built. Re-arming re-adds the collision.
- 4 behaviors armed in one 36h window, 3 within seconds/minutes of shipping, no measurement gap → every regression is entangled, every fix a guess.

Jun 30 — completion-ceiling (near-dead problem)
- 7c6a6a4/d2ac207 completion-combined-ceiling armed — but over-par is ~0% live (1 leg in 591). Solving a near-dead problem.

---

WHAT THE FULL ARC SHOWS (do not reduce to one stat):
1. Two silent P0s — order CREATE (Jun 19) and CANCEL (Jun 25) both 410'd, silently failing for unknown stretches. Any P&L or fill analysis spanning those windows is contaminated by infra that wasn't working.
2. Fixes broke adjacent things — the UnboundLocalError chain (c03e010 → 22f4f57 fixing what it left two lines down), fv-anchor thrash (4× arm/disarm), ITF live ref-error.
3. Recurring bug class (3×): PaperApi-only attribute read on the live class (fv-anchor, ITF volume_tracker, pair-governor last_trade_price_at_post). When the same fix recurs, it's a SYMPTOM.
4. Arm-spree pattern — Jun 26 (5 flags/night) and Jun 29 (4 flags/36h), no measurement gap between armings. This is why regressions are entangled and the flag-bisect exists at all.
5. The whole month is ENTRY-MECHANIC plumbing — join-the-bid, staircase, repost, depth-governor, gun-detection, ITF-borrow, pair-governor. Nearly every deploy is about WHERE/WHEN a bid rests and fills. The problem is entry mechanics, and the record is 45 days of entry-plumbing that kept breaking itself.
6. Green (Jun 26–28) is the whole six-pack at once, un-isolated. "Restore green" restores a bundle, not a clean single lever — and pair-governor (part of green) can't safely re-arm (duplicate-buy).

---

## 5. THE OPERATOR'S THESIS (his words, hold them)

- The bleed is the games where we fill ONE side, at a BAD price, and that side is the falling knife — NOT the clean under-100 pairs.
- Combined entry price is a METRIC to gauge getting in cheap enough not to need an overswing to exit. Not a target.
- THREE WINDOWS to hit the exit: (1) premarket drift, (corridor), (2) in-match. Only Window 2 is dictated by the game. The dog CAN cash on drift in Window 1 (cheap + room + small band) — a possibility our shit entries fail to capture. Nothing is one-way: all windows live for both legs; entry quality determines how many are reachable.
- Discount vs distortion: buy at discount → exit reachable across windows. Buy at distortion (over fair) → only Window 2 reaches it → rides to 0 on reversal.
- One side filling should force reassessment of the other position.
- 30 days of analysis already settled the better entry method. "30 days later it shouldn't be confusing."
- Whatever's built either isn't good enough or is missing the other end. Everything must connect.
- Yesterday's learnings TRUMP earlier days.

---

## 6. THE GUN-CANCEL DEFECT (operator-flagged Jun 30, confirmed in data)

- Only 1 match-live resting-cancel fired all day Jun 30 (KOPCHO 14:20, graced=true).
- If a side didn't fill, its unfilled bid STAYED OPEN — both cancel triggers broken: (a) T-15m ENTRY_BUFFER keys on SCHEDULED start, a stale/drifting placeholder (T51); on late-running games the buffer elapsed at stale-scheduled-T-15m hours before the real gun. (b) match-live cancel keys on sustained_flow K=3, which can't latch thin books → never fires.
- Evidence: OSOWAL-class positions filled 8-10 HOURS after scheduled start — bids that should've been cancelled, filling into stale/live markets.
- An ENTRY-side defect distinct from exit-reach: we hold open bids we should have killed, and they fill into live play at bad prices. Status: flagged, going to Plex.

---

## 7. WHAT WE CANNOT SEE (don't pretend to)

- June 6-18: no commits, no handoff in this branch. ~2 weeks invisible.
- The master plan (OMQS_MASTER_PLAN.md) and journal (/mnt/transcripts/journal.txt, E186 tracker): NOT in this repo. On the operator's machine. The "live-state entry instrument" fuller spec lives there.
- June-5 lineage (14f045d5): NOT an ancestor of blend/agent-derivation. Partial branch disconnect.
- Live VPS runtime (orders/fills/tick-tape): only via CC. REST is ground truth; per-minute candle too coarse.
- .claude/ validation scripts (mirror_joint_ev, build_conservative_entry): cited but not pushed.

---

## 8. INFRASTRUCTURE

- VPS root@104.131.191.95 | cd ~/Omi-Workspace/arb-executor | executor live_v4.py (~7,300 lines) | config config/deploy_v5_live.json
- Repo github.com/OMIGROUPOPS/Omi-Workspace, working branch blend/agent-derivation.
- SECURITY [UNFIXED]: VPS .git/config embeds a live plaintext GitHub PAT with push rights. Flagged repeatedly, never rotated. Recommend rotate + SSH/credential-helper.
- Accounting: report as cash + mark vs baseline, never cash-only. Current equity ~$2505 (Jun 30 dump). Reconcile baseline against the dump.
- Three-agent loop: Fable (strategy/verify/drive) → CC (executes on VPS) → Plex (adversarial gate). Operator relays. One concern per CC prompt. Plex reads pushed artifacts via public raw URL.
