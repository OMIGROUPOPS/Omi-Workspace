# Entry-Side Patch Dispatch — 2026-07-03 (HOLD deploy)

Branch `blend/kalshi-occ-fallback`. Six items, entry-side only. **All code gated default-OFF = byte-identical; config unchanged; bot NOT restarted (HOLD for one go).** Pricing derives from the 9.3M-row PMU record + raw ITF trade corpus — no hand constants. Tests: `tests/test_aim_dispatch.py` (24/24 PASS incl. `leg2_never_over_goal` + byte-identical-off guards, clean module import).

---

## (0) AIM TABLE — `docs/policy/aim_table.json` (supersedes flat 3¢)
Per category × price-bucket: the **aim = fillable DIP below current** (the discount a resting bid is *paid* to the gun, A49), NOT FV. Derived from PMU (`min_yes_ask_forward_to_match_start` = how deep the ask dips before the gun; 2.53M premarket rows) for the 4 tour cats; raw gzipped trade CSVs for ITF (no PMU coverage).

| cat | dip med | fill% | spread | → **faller_depth** |
|-----|--------:|------:|-------:|-------------------:|
| ATP_MAIN / WTA_MAIN | 2–5¢ | 80–89% | 1¢ (tight) | **2¢** |
| ATP_CHALL / WTA_CHALL | 4–7¢ | 87–92% | 2¢ | **3¢** |
| ITF_M / ITF_W | 7–32¢* | 93–99% | wide | **4¢ (capped)** |

**Honest finding — the flat 3¢ was already close for tour.** per_cat_depth is a *modest* refinement (MAIN 2 / CHALL 3), not a revolution. **ITF caveat (load-bearing):** the raw-trade ITF dip medians look huge (7–32¢) at 97–99% fill, but several buckets show drift −12 to −16¢ = **the side collapsed** — those "dips" are contaminated by directional collapse (the falling-knife = last night's fragile ITF shape). The harness couldn't extract ITF spread, so it capped ITF at 4¢ rather than trusting a 20¢ dip. **That cap is right; deepening ITF beyond 4¢ needs a spread-clean, collapse-separated re-derivation before it's safe.** The wide-spread-deep-fill thesis is directionally supported (fill% 97–99%) but the *magnitude* is not yet trustworthy.

## (1) `leg2_reshuffle` (gated) — sequenced re-aim, NOT a cap
- **Entry** (`_v4_entry_anchor`): leg-1 (riser, anchor≥50) posts **at best bid, never vetoed** for projected combined; leg-2 (faller, anchor<50) posts at aim depth — **except** both best bids already sum ≤ `combined_goal` (97) → both at bid immediately.
- **Re-aim** (`_v4_manage_resting_inner` walk): once leg-1 (sibling) has **filled at X**, every leg-2 walk clamps `new_target ≤ min(aim dip, goal − X)` → combined ≤ goal, **re-derived per walk** (closes the ceiling's checks-once hole). Bid stays resting — only lowers/holds, never pulls. Logs `leg2_reshuffle_reaim`.
- Pure fn `_reshuffle_leg2_target` proven: for all X∈[1,98] × anchor × depth, `X + target ≤ goal`. **leg-2 can never complete over goal.**

## (2) `per_cat_depth` (gated)
`_v4_entry_anchor`: the per-side dog-deepen uses `_aim_faller_depth(cat, anchor)` from the aim table instead of the flat `dog_dip_offset_cents`. Missing cell → falls back to flat 3¢ (never raises). OFF → flat 3¢, byte-identical.

## (3) Wall-starvation (−$13.60 class) — MEASURED, `wall_starvation.tsv`
**It is NOT mainly hard queue-wall.** Of the 12 half-armed games (settled loss −$14.90; 4 still open):
- **REAL-QUEUE — 3 games, only −$1.10 settled** (BROTUB; MOESHA+BARKRE open): sell-flow prints at our exact price but behind a 3k–46k wall.
- **NEAR-MISS — 5 games, −$7.55 (incl. NEDSMI −$6.70):** favorite sibling rested **1–2¢ below live sell-flow** — a tiny reprice-up completes the pair.
- **STALE-DEEP DESERT — 4 games, −$6.25:** our bid sat 13–40¢ below the live market. Unfillable, correctly; buying up completes a combined>100 (negative arb).

**Patch specs:** (1) NEAR-MISS = reprice the favorite UP to the sell-floor, capped `≤ 99 − leg1_basis` — **this is exactly the completion-ceiling + a +1/2¢ sell-floor trigger** (biggest ROI, recovers the −$6.70). (2) REAL-QUEUE = a wall-jump (`bid+1` ahead of a >K·size wall). (3) DESERT = do not chase — fix is upstream (stale anchor) or hold-both-to-settle. *These are next-cycle specs, not built this dispatch (entry-side scope).*

## (4) In-play chase — census + `freeze_at_gun`
- **(a) ALCCLA (`KXITFWMATCH-26JUL03LOPCLA`, our 88¢ LOP leg):** a **premarket WALK-UP** — posted 61¢ @10:39, walked **+26¢ to 88¢** @10:45 chasing the climbing book, filled 10:47. `match_live_detected` **never fired** (no gun all session). It was a walk in mechanism but ~3.7h pre-gun.
- **(b) Census (`chase_census.tsv`):** STATIC 109 legs **mean FV +1.89¢** vs CHASED 27 legs **mean FV −1.22¢** — **chasing costs ~3¢ of fill-vs-fair.** Post-*latch* chasing is essentially null (1/136) because the walk's `if _live: return` already stops it; the damage is **premarket walking**.
- **(c) `freeze_at_gun` (gated) built:** at the live latch, no fresh entry post (`_v4_entry_anchor` returns None) and the resting bid is **HELD static** (dip-fillable) instead of live-cancelled — the validated thesis (77/136 overnight fills came post-gun on the dip to a static bid). **Faithful-but-honest caveat:** keyed on the volume-burst latch this bites only near the real gun; per the census the actual chase damage is *premarket* walk-up, which the latch can't see. **The census-justified real lever is a `premarket_walk_cap`** (cap walk-up distance — would have stopped ALCCLA's +26¢). Recommended as the immediate follow-up; not built here (stayed within the 6-item scope).

## (5) Completion-trio audit vs the new design — REPORT ONLY (nothing changed)
`completion_combined_ceiling` lives **only** in `_completion_target`, called only from `_attempt_completion_reprice` (the leg-1-fill → reprice-sibling-**UP** path). It bounds the completion pay-up to `V4_PAIRED_BASIS_CAP − leg1_basis`.
- **Redundant where** leg-2 is resting and gets reshuffle-re-aimed: leg2_reshuffle binds combined tighter (goal 97) and earlier (entry-side, lower-only) than the ceiling's 99.
- **Complementary where** the favorite sibling must be repriced **UP to fill** (exactly the item-3 NEAR-MISS class): leg2_reshuffle only *lowers* leg-2 (never pays up), so it **cannot complete a starved favorite** — completion+ceiling does. **Verdict: NOT a disarm candidate.** Keep both — reshuffle = entry-side lower-only combined bound; ceiling = completion-side pay-up cap. They cover disjoint directions.
- **The CASOSO 112 leak is neither's fault to fully close:** both legs filled as *independent simultaneous entries* (17+95), never through completion; reshuffle's walk-clamp catches it only if leg-2 is still resting when leg-1 fills. Simultaneous independent fills at rich prices are the **residual race** — flagged, not closed.

## (6) Grade-vs-result validation — `grade_vs_result.tsv` (standing check)
**Monotonicity PASS:** per-game avg net A **+1.19** ≥ B **+0.73** ≥ C **−0.20** ≥ D **−0.28** ≥ F **−1.26**; A aggregate **+$13.05 > 0**. No inversions — grades ordered, **A pays.**
**A-standard verdict — the data refutes tightening A:** among fully-filled pairs, those that were **NOT** both-legs-FV-positive settled *better* (net +$5.95, win 0.73) than both-FV-positive (net +$3.35, win 0.55). **Requiring both-legs-FV>0 would discard winners.** combined≤97 + clean-green exit is the sufficient A-shape (6/6 settled, +$5.05). **Keep the letters. FV is the yardstick, not the target — confirmed empirically.** Biggest standing bleed = **F half-armed settlement losses −$17.65** (the class to watch).

---

## Deploy sequence (HELD — awaiting one go)
Nothing armed. To deploy: set in `config/deploy_v5_live.json` and restart (tmux `live_v4`, ulimit 262144):
1. `per_cat_depth: true` (lowest risk — modest tour refinement, ITF stays 4¢).
2. `leg2_reshuffle: true`, `combined_goal: 97` (entry sequencing + re-aim).
3. `freeze_at_gun: true` (hold-through-gun; note near-inert vs premarket walk — see §4c).
Recommend arming (1)+(2) first, shadow one slate, then (3). `aim_table.json` must be present (it is, `docs/policy/`).
