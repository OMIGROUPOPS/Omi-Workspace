# SEALED — ATP_MAIN range_final staircase entry table

Sealed 2026-06-15 (C-ATPMAIN-STAIRCASE-SEAL, Plex-ratified). **Canonical record, NOT a deploy** — the production bot stays on boot SHA `0499570`; this surface is sealed-canonical but not live until the operator times a restart.

## 0. Scope — ATP_MAIN ONLY
This seal covers **ATP_MAIN only.** The other three categories remain on `entry_table_percell.csv` (the current maker). Scope rationale: under the gated re-validation (below), **only ATP_MAIN cleared both binding bars** — WTA_MAIN failed ROC (ΔROC −0.37), ATP_CHALL failed FILL (Δfill +14.1pp), WTA_CHALL failed both and is genuinely thin (class A). Deepened cells: **63 / 90** (27 held-current via the n<20 / EV≤0 gate).

## 1. Identity (pinned content-sha256)
| File | sha256 |
|---|---|
| docs/policy/range_final_ATP_MAIN.csv | `0809dc4ce379fe6210271dcf58effd7e9f1b5457ca0aab7d8aee1ab63cc1f2fc` |
| docs/policy/range_final_walk_schedule.json | `624697fd92916a932f83ef421a0d4f166db0b348544ad4f1504e81d51681db49` |

- range_final_ATP_MAIN.csv authored at commit `3c2161c` (build `analysis/exit_charts/build_range_final.py`).
- range_final_walk_schedule.json **pre-committed at `3a701ba`** (the hypothesis, registered BEFORE the gated walk — not tuned to move ROC).
- DIRECTION-FREE: no direction-conditioning anywhere (premarket direction died at Cut 0; in-match momentum coin-flip). Pure range/depth.

## 2. Validation provenance (gated α/β/γ — both bars cleared)
- **Result (ATP_MAIN):** ΔROC **+0.52pp** (10.38 vs current 9.86) → ROC bar PASS (win ≥ +0.30); Δfill **−4.0pp** (72.3% vs 76.2%) → FILL bar PASS (within ±5pp). Both binding bars cleared.
- **α — schedule pre-committed `3a701ba` before the walk:** knots 240/210/180/150/120/90/60/30/10, depth deep_target→anchor-1, most aggressive final 10 min, 2-min intent buffer. Hypothesis registered first, not fitted.
- **β — latch cutoff:** the tail cancel keys on `_is_match_live` (volume-burst latch, `live_v4.py` match_live_cancel @ commit `0499570`), NOT wall-clock 2-min-before-scheduled-start; delay-proof. Sim cutoff = onset (latch), no wall-clock floor.
- **γ — per-cat bars** reported, not aggregate (ROC: win ≥+0.30 / no loss >−0.20; FILL: ±5pp). ATP_MAIN only passes both.
- **Predecessor finding:** `3c2161c` (range_final commit-for-review); gated findings `2147d3b` (`docs/policy/range_final_GATED_FINDINGS.md`).
- **Engine sanity:** ATP_CHALL CUR real_roc 11.24 == committed `entry_lift_permatch` (walk sound); ATP_MAIN baseline 9.86 under the deployed `_full` exit (reseal-superseded; 18.48 was under the old probe).

## 3. WTA_CHALL — class-A disposition (held-current, NOT deepened)
Class-A trace found **no pipeline bug**: `categorize()` (`data/scripts/cell_key_helpers.py:42`) is a pure ticker-prefix matcher with no category drop; PMF WTA_CHALL (649 events ≈ 1,298 legs) faithfully matches the g9_metadata source (1,318 WTA_CHALL legs). The thinness is **genuine** (WTA Challenger was small in the historical g9 window). WTA_CHALL stays on `entry_table_percell` — not deepened, not in this seal.

## 4. Deploy status
**NOT deployed.** Wiring ATP_MAIN entries to this staircase + restarting the bot is a separate operator-timed step. Until then the bot runs `entry_table_percell` for all cats (boot SHA `0499570`). See exit-surface seal at `data/durable/exit_surface_gated_optima/LOCKED_DOWN.md` (separate artifact). Mirror cadence per `docs/policy/canonical_tree.md`.

## 5. Deploy-guard abort triggers (canonical spec)

**Pre-registered before deploy (anti post-hoc relaxation).** Evidence: `docs/policy/range_final_ATP_MAIN_ABORT_VALIDATION.md` + fills table `docs/policy/range_final_ATP_MAIN_abort_fills.csv` content-sha256 `4e4c15534c6cb6a2f38802760b584c101bbf1f1b245e2631d7db075cc678a92e` (Plex-ruled against evidence commit `12d8deb`). N: 4,975 attempts / 3,595 fills / 3,586 rolling-10 windows.

| # | trigger | locked bar | status |
|---|---|---|---|
| **T1 OFFSET** | ≥3 of the first 10 fills with residual < −1c, where `residual = observed_offset − regime_expected` (regime_expected per the §-evidence per-regime table, walk-derived median fill_offset). | val FP **0/3586**, **CONDITIONAL** | CONDITIONAL on the offset≥1 clamp landing as a deploy-prerequisite (see §6) |
| **T2 FILL-RATE** | **fills ≤ 6** over the first 10 ATP_MAIN engagement attempts (rate < 62.3% = 72.3% point − 10pp; denominator = engagement attempts, first nonzero placement = t=0). | **LOCKED unconditional** | — |
| **T3 ROLLING-ROC** | **rolling-10-fill ROC < 0** — filled legs only, chronological by `match_start_ts`, stride-1 (overlapping), simple capital-weighted (`Σmk_ret/Σmk_cap`), evaluated after the first 10 staircase fills (val min +7.78). | **LOCKED unconditional** | val FP 0/3586 |
| **T4 WALK-STEP** | out-of-order placement OR depth-increase vs the knot sequence `[240,210,180,150,120,90,60,30,10]` (`range_final_walk_schedule.json` content-sha256 `624697fd92916a932f83ef421a0d4f166db0b348544ad4f1504e81d51681db49`); depth must be monotone non-increasing toward start. | **LOCKED**, zero tolerance | — |

**Abort action (pre-authorized, no further gate):** hot-revert `shadow_mode=true` if supported, else restart the bot to boot SHA `0499570`. Any one trigger firing → abort.

## 6. Validation parity gap — anchor-1 floor (BLOCKING deploy-prerequisite)

The validation walk enforced **offset ≥ 1** (bid ≤ anchor−1) only in the simulation (`analysis/exit_charts/abort_validation.py`: `D = max(1, ...)`). **Live code has no such invariant:** `_reprice_target` (`live_v4.py:3166`) and `_fallback_order` (`live_v4.py:3175`) clamp to `max(1, best_ask − 1)` — a floor on **absolute price (ask−1)**, NOT on offset-relative-to-anchor (`live_v4.py` blob `1912d8bc`). When `best_ask > anchor`, the clamp posts at `ask−1`, which is shallower than `anchor−1` (offset < 1 vs the placement anchor).

**Consequences:**
- The sealed **+0.52pp ΔROC and the §5 T1 0% FP are SIM-CONDITIONAL** on an `offset ≥ 1` (bid ≤ anchor−1) clamp existing in the live staircase placement path.
- That clamp is a **BLOCKING deploy-prerequisite.** Until it lands (a separate commit, pending the operator's path decision), the ATP_MAIN staircase must NOT be wired live.
- **The operator MUST read this §6 before timing any restart.** See §6 of the Z evidence doc (`range_final_ATP_MAIN_ABORT_VALIDATION.md`) for the code-pointer derivation.

---
*Seal-touching amendment (C-ABORT-SEAL-Y). No history rewrite post-merge (ledger #30). §5/§6 pre-registered before deploy.*
