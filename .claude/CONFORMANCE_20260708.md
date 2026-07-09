# CONFORMANCE AUDIT — 2026-07-08 (~10:00 pm ET; board #4; full pass, pulled forward from 07-14)

**Method:** read-only vs the running process (**PID 1656151, blob `fdba24e`**, C-GUN-PERSIST lineage). Referee = today's jsonl + exchange truth + `config/deploy_v5_live.json` (83 keys) + the ratified surfaces (recut_cells, anchor hierarchy, dynamic-S ruling). Since the 07-07 sweep: **8 gated deploys, 3 rulings, 2 new surfaces.** Producer: `/root/conformance_pull.py`.

## §1 CONFIG vs CODE

| finding | detail | verdict |
|---|---|---|
| Orphaned config keys (in file, never read) | `exit_band_resolution`, `version` | `version` = metadata OK; **`exit_band_resolution` = DRIFT-1 (remove at next config-touch)** |
| Code defaults not in config (25) | mostly deliberate gated-OFF defaults (`monotonic_cut_*`, `freeze_at_gun`, `kalshi_occurrence_fallback`, `expression_invariant` absent=OFF **as ruled** ✓) | **DRIFT-2: `conception_horizon_hours` (the T-8h bound!) lives as a code default — make the LAW an explicit config key.** Others acceptable-implicit |
| Dead-flag review (board #9-adjacent), verdicts | `per_match_clock_shadow=TRUE` — shadow logging for a flag armed since 07-06: **RETIRE at next config deploy (the one live archaic-ARMED flag — this sweep's finding, same class as join_trial)** · `fv_anchor_scenarios_enabled=false` + `round5_detector_enabled=false`: **REMOVE keys (dead legacy)** · `pair_governor_scoot=false`: **KEEP (tombstone)** · `riser_post_revision=false`: **KEEP (re-arm pending Plex bounce)** · `join_trial_mode=false`: retired ✓ | verdicts filed |
| New-law flags vs deploys | `fused_gun_enabled=true` ✓ · `anchor_hierarchy_enabled=true` ✓ · `walk_cap_honest_anchor=false` (staged, shadow) ✓ · `completion_all_cells=true` (armed lineage d2ac207 06-30, legitimate) ✓ | conforming |
| Walk-cap staged values vs the Plex ruling | ITF_W 20 / ITF_M 14 / ATP_CHALL 2 / WTA_CHALL 2 / mains 1 | **EXACT match** ✓ |

## §2 CODE vs TABLES

| surface | consumer state | verdict |
|---|---|---|
| `recut_cells.json` (ratified aim surface) | **NO consumer in live_v4 — BY DESIGN** (AIM_V2 gated OFF; the ruling armed the KEY, not the ramp; arm gates unchanged) | conforming (the ramp wires it) |
| `aim_table.json` | 15 code refs, live (shadow aims on 488 aim_shadow lines today) | conforming |
| Band [5,95) | 4 sites (placement clamp / walk pre-cancel guard / audit flag / cross bounds) — same literals | conforming; **0 out-of-band resting buys now** |
| S-lines / dynamic-S | not in bot (descriptive/renderer-side, correct) | conforming |
| **THE 97-BASIS CENSUS, CURRENT** | The cap-arithmetic is not drift — it IS the goal law: `combined_goal(97) − leg1_basis` **UNIFIED on every resting/reprice/completion branch** (the 99 ceiling explicitly DEAD in code comments); sites: `_reshuffle_leg2_target`, completion-goal breach checks, `reaim_sibling_arrival`, all reading `combined_goal` config=97. **TODAY: 93/99 sibling placements (94%) price at exactly 97−basis — UP from the era's 77%.** | **NAMED, not convicted: under the S-tier provenance clause every one is S-INELIGIBLE BY CONSTRUCTION — the completion-pricing law itself is the S-blocker; the cell-keyed aim ramp is its ratified replacement. DRIFT-3: this is the standing INTERIM-ARCHAIC census — re-print nightly until the ramp arms.** |

## §3 RULINGS vs RENDERERS

| ruling | renderer state | verdict |
|---|---|---|
| Dynamic-S formula (Σ own W1-close − edge_p50) | `position_grade.py` implements it verbatim; first cut ran tonight (day close) | conforming |
| Provenance clause enforcement points | position_grade `provenance()` (CAP-ARITH → S-INELIGIBLE; EBEDUP demoted live tonight) + the front-page clause | conforming |
| anchor_source on window stamps | `scalp_filled` ✓ (first live row: ZIVMIK, `te_honest_datemiss`) — **`entry_filled`/`exit_filled` do NOT carry anchor_source: DRIFT-4 (extend the stamp at the next defect-class deploy)** | PARTIAL |
| THE GRID labels (ITF exit-borrow) where grades print | POSITION_GRADE ✓ († per row), SEQFLOOR_RECUT ✓, SLATE cut ✓ — **the old SLATE cross-tab machinery is NOT dynamic-S/GRID-aware: DRIFT-5 (renderer refresh owed before the weekly full cross-tab re-run)** | PARTIAL |

## §4 TAPE COLUMNS RE-RUN (8 deploys owed) + archaic sweep (pulled forward)

Prior 23 rows, today's fires (post-respawn file): leg2_reshuffle_reaim **×2,931** (goal 97 law) · buy_blocked_position_full ×47 + conception_halt ×17 · reconcile_exit_topup ×20 · complete_cross_skip ×18 (cross ×0 — natural) · window_open_set ×336 · bid_ex_self ×488 (=aim_shadow ×488, C47 measurement law) · expression_clamped **0** (OFF as ruled ✓) · premarket_walk_capped ×1 · v4_repost_hold_same_price ×84 · match_live_unlatched ×3 · adoption_true_basis ×21 · order_error ×24, **410-class 0** · would_skip_walled_post ×65 · kalshi_occ_observe ×92 · v4_exit_posted ×206 (sealed bands) · C50 enforced on ALL of today's 6 deploys ([4/4] two-file law OK each).
**New-law rows (born since 07-07), all live-proven today:** fused gun (17 fired + 18 rebuilt at boot) · fingerprint (23 re-adoptions, `fingerprint_in_manual` 0 across 58 audits) · horizon (342 defers, beyond-horizon 0) · anchor (17 clock_liars, 7 datemiss_36h) · gun-persist (rebuilt n=18 = fire log, post-fire placements 0) · band clamps (59+7 refusals) · `buy_placed_post_fire` armed (0).
**UNPROVEN-LIVE movements:** `never_marketable_clamped` **FIRED today (PLADIG-PLA 8:00:59 pm, ask=1 degenerate-book clamp) — row CLOSES, live-proven** · `hold_to_settle` still 0, stays with detector · `/tmp/live_v4_TRIPWIRE.json` **checked this pass: ABSENT (good)** — the 07-07 stamped gap closes · C50 bootstrap long past (strict on every deploy today).
**Archaic sweep verdict: ONE archaic-ARMED flag found — `per_match_clock_shadow=TRUE`** (shadow logging for a flag armed 07-06; the join_trial class, DRIFT-6/retire). No INTERIM-ARCHAIC implementation surfaces beyond the named 97-basis law (§2).

## THE DRIFT LIST (the follow-up queue)
1. **DRIFT-1** remove `exit_band_resolution` (orphaned key) — next config-touch deploy.
2. **DRIFT-2** `conception_horizon_hours` explicit in config (a LAW living as a code default).
3. **DRIFT-3** the 97-basis census (94% today) re-prints nightly until the cell-aim ramp arms — the standing INTERIM-ARCHAIC surface.
4. **DRIFT-4** anchor_source on entry_filled/exit_filled stamps (scalps only today).
5. **DRIFT-5** SLATE cross-tab renderer refresh (dynamic-S + GRID aware **+ COMBINED-PRICE CLAUSE: every combined prints its dynamic floor alongside — fixed-line rates barred as headlines**) before the weekly full re-run.
6. **DRIFT-6** retire `per_match_clock_shadow` (archaic-ARMED) + remove `fv_anchor_scenarios_enabled`/`round5_detector_enabled` keys — one config-hygiene deploy takes DRIFT-1/2/6 together.

**Cadence:** tape columns POST-ANY-DEPLOY (this run covers the 8 owed); next full weekly 2026-07-15.
