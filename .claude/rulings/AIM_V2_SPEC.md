# AIM_V2_SPEC — regression aim table (per PLEX_REGRESSION_RULING ①, 2026-07-06)

**Prior art (C45):** the median table (`fv_aim_build2.py` → `/tmp/fv_shapes.json`, 07-06 — the schema this replaces drop-in); TIME_AXIS_PROOF.md (07-05, aim_table_t.json lineage + the anchor debt); ONE_AIM_FIX_20260706.md Job-2 (the frontier fail + model limits this spec answers); census Axis-2 amendment (role paths); A49 (aim = fillable dip, FV = yardstick); the flat aim_table.json (deployed baseline). Inherited failure mode NAMED BY PLEX: the median script's **silent neighbor interpolation** (`shape_at` ±4-bin search with no flag) — this spec forbids it everywhere, and the discipline is imposed on the median script effective 2026-07-06 (see §5).

## 1. Schema — drop-in replacement for the median table
Keyed identically: `"{CAT}|{BUCKET}"` → `{Tbin: cell}` (BUCKET = 20¢ price quintile 0–4 of CURRENT price; Tbin = 10-min bins to the bell, 0–48; bell = unambiguous tape onset, honest-clock era rows preferred). Cell fields (all first-class, never stripped):
```json
{"n": int,              // samples in cell (honest-era n_h + card-era n_c reported separately)
 "n_honest": int,
 "drift": float|null,   // fitted E[bell_px − px | cell]  (the FV component)
 "dip":   float|null,   // fitted q-quantile of remaining-dip (the aim component; q a build param)
 "resid_sd": float|null,// residual spread of drift fit — first-class per the ruling
 "pooled_w": float,     // 0..1 shrinkage weight toward the cat-level path (∝ n)
 "null_reason": str|null // "below_floor" | "no_data" — below-floor cells are PARKED, not interpolated
}
```

## 2. Estimator
- **Monotone splines / GAM on log-odds per bucket:** fit `logit(px/100)` trajectories vs T within (cat, bucket, role-implied-by-bucket); drift and dip derived from the fitted path, with the T-monotonicity constraint (paths converge to the bell price; remaining-dip magnitude is non-increasing in T-to-bell).
- **Hierarchical pooling:** each (cat, bucket) curve shrinks toward the cat-level curve with weight `pooled_w = n/(n+k)` (k = pooling constant, default 50); pooled_w reported per cell.
- **HARD minimum-n gate: floor n ≥ 30 per cell.** Below floor → all estimates null, `null_reason="below_floor"`, cell PARKED. A consumer receiving null must fall back to the deployed flat aim — **never to a neighboring cell without an explicit `borrowed_from` marker.**

## 3. Coverage-defined re-run trigger (accumulator contract — not vibes)
Target cells = the fix's habitat: **Tbin ∈ [12, 36] (2h–6h pre-bell) × all buckets × {ITF_M, ITF_W, ATP_CHALL, WTA_CHALL}**. Trigger fires when **≥50% of target cells reach n_honest ≥ 30**; the accumulator then re-runs the derivation automatically and writes `SHAPE_RERUN_REPORT_<date>.md`. Coverage is visible nightly in `data/shape_corpus/coverage.json`.

## 4. Z-SCORE (per Ruling ④ — own build, own gate)
`z = (current_px − path_px(cat,bucket,T)) / resid_sd` — how far the leg trades from its similar-games path. **Own flag `aim_zscore_shadow`, default OFF, shadow-first** (riser_post_revision / C-KALSHI-OCC observe precedent): logs `aim_zscore` rows only, zero behavior. Consumes whichever table version is live (median now, V2 when it lands) — resolved at read time. Null cells → no z, no log (no silent borrow). Consumer semantics (divot qualification / re-aim modulation) are a LATER build behind its own Plex gate.

## 5. Discipline imposed on the median script TODAY
`fv_aim_build2.py` (and the accumulator's embedded derivation): `shape_at` neighbor search is now **explicit** — returns `(cell, borrowed_from_bin)` and any consumer logs/propagates `borrowed=True`; cells with n < 30 emit null (parked) rather than participating in neighbor search. Replay outputs count borrowed-cell usage as a first-class column.

## 6. Standing arm bars (restated verbatim from the held conditions)
Beats the −$20.31 verdict on the new basis · walk/repost interaction explicitly modeled — **the riser's bar-(e) erosion pattern is the test** (share of fills above first-post < 25%) · the walk-cap honest-window anchor ships with or before any arm. Validation = `aim_v2_harness.py` (walk-forward by week, honest-filtered/reweighted, card-era flagged; census-161 secondary confirmatory OOS; Lane-1 = joint gap shrinks / lazy-leg-1 shrinks / participation holds). Then Plex. Then the rolling slate.
