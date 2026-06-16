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
