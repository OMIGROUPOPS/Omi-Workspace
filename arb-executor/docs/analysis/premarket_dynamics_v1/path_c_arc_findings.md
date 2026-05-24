# Path C arc — feature-conditioned entry refinement: a structural negative, with the deployable lever isolated

**Date:** 2026-05-23
**Universe:** atlas — 14,033 N (ATP_MAIN 4,137 / WTA_MAIN 3,683 / ATP_CHALL 5,326 / WTA_CHALL 887).
**Arc:** Path C Phase 1 (predictor) → Phase 2 (offset modulation) → Phase 3 corrected (execution-mode
switching), framed against the contemporaneous Path B v4 positive result (ROADMAP T47). **Pre-realism**
throughout (B25 0.5–0.7× discount applies to every number below). This document closes the empirical
premarket-dynamics strategy arc.

---

## Section 1 — The question, and the answer

**Question (Plex Round 7, Tier 1):** the Path B static per-regime maker-placement table is uniform within
a (category × anchor_regime) cell. Every event in a cell gets the same offset. But events differ — some
have a wide paired-arb gap at T-4h, some show heavy taker buying, some a wide spread. **Can a per-event
fill predictor, conditioning the placement on observable T-4h features, beat the static table?**

**Answer: no — not through any tested channel.** A predictor with genuine out-of-sample signal (Phase 1
holdout AUC 0.73) fails to lift realized ROI whether it is used to (a) gate placement on/off (Phase 1,
−2.8 to −2.9pp), (b) modulate the offset size by predicted fill probability (Phase 2, +0.08pp gross =
noise), or (c) switch execution mode per-cell on the drift gradient (Phase 3 corrected, −0.24pp net). The
binding constraint is **structural, not informational**: the locked atlas fixed-profit exit caps what any
entry-side refinement can be worth (Section 6). The lever that *does* move the number is the **static
per-cell offset itself, re-optimized on the net-PnL objective** — Path B v4, +1.02pp (Section 5). Path C
is a clean, decisive negative that simultaneously proves the predictor works and proves the architecture
can't monetize it on the entry side.

---

## Section 2 — Phase 1: the predictor is real (holdout AUC 0.73)

Phase 1 fit a 3-feature logistic for `drift_reached_bid` (did min(ask, last-trade) over T-4h→T-20m reach
the per-regime target bid) on T-4h observables: `paired_arb_gap_cents`, `initial_spread_cents`,
`taker_imbalance_30min` (the last sourced from the causally-correct pre-T-4h window of
`per_minute_features`; pure-numpy AUC / IRLS / CPCV / permutation since no sklearn on the VPS).

- `drift_reached_bid` = **3,983 / 14,033 (28.4%)** — exactly Path B v3's fill count.
- **CPCV** (28 paths, 8 folds k=2, year-week tournament blocks, 2-week embargo): **mean AUC 0.6625 ± 0.0418**.
- **Holdout** (Mar–May 2026, 6,047 events never in CPCV): **AUC 0.7298** — clears the 0.62 bar.
- `taker_imbalance_30min` dominates the holdout AUC (permutation drop 0.022, ~6× the others) with a
  **negative** coefficient — more net buying at T-4h → lower P(reaching a below-anchor bid), mechanically
  coherent (taker buying pushes price up, away from the bid). `paired_arb_gap` and `initial_spread` are
  positive, significant, smaller. A ≥5¢ paired gap at T-4h roughly triples within-cell fill probability
  (e.g. ATP_MAIN r75_84: 31.6% → 73.5%, AUC 0.747).

**The signal is genuine and out-of-sample.** That is what makes the downstream negatives load-bearing
rather than a failed model: the refinements below fail *despite* a working predictor.

The same Phase 1 run already surfaced the first crack. Two binary skip-gates — place only on high-P
events — both **lowered** ROI: Rule A (≥2/3 thresholds, place 7.1%) 9.17% (−2.94pp); Rule B (P>0.5, place
20.6%) 9.36% (−2.75pp), vs v3's 12.11%. Because v3 already falls back to a costless taker-at-anchor on a
miss, *skipping* low-P events only forgoes the cheaper fills they would sometimes get — it cuts volume
with no offsetting gain (LESSONS A42). Phase 1's recommendation was therefore explicit: the predictor's
value, if any, is in **offset modulation**, not skip-gating — which Phase 2 tested.

---

## Section 3 — Phase 2: offset modulation is noise (+0.08pp gross)

Phase 2 mapped P(drift) → bid aggressiveness: place a **larger** offset when the predictor is confident
the bid will fill anyway, a **smaller/safer** offset when not. Four P-threshold parameterizations were
swept (primary 0.65/0.35, narrow 0.70/0.30, broad 0.60/0.40, two-tier 0.50), each splitting the corpus
into aggressive / neutral / conservative tiers and applying a tier-specific offset on top of the v3 table.

| Variant | gross PnL | gross ROI | vs v3 repro |
|---------|-----------|-----------|-------------|
| v3 repro (place all, v3 offsets) | $8,098.50 | 12.105% | — |
| primary_065_035 | $8,153.00 | 12.183% | +0.078pp |
| narrow_070_030 | $8,118.20 | 12.131% | +0.026pp |
| **broad_060_040 (best)** | **$8,162.70** | **12.194%** | **+0.089pp** |
| twotier_050 | $8,150.90 | 12.176% | +0.071pp |

**The best variant adds +0.089pp gross — noise, well inside run-to-run jitter, and pre-realism it
vanishes entirely.** Per-cell dominance is only 22/36 (the conditional rule does not even beat v3 in 14
cells). The mechanism: modulating the offset changes *which* events fill and at what discount, but the
discount only matters on hold-to-settlement outcomes; on the majority triggered-exit outcomes the realized
PnL is +X regardless (Section 6). Confidence-weighting the offset reshuffles entry prices without moving
the payoff that dominates the blend. **Negative — not promoted to policy.**

---

## Section 4 — Phase 3 corrected: execution-mode switching is negative net (−0.24pp)

Phase 3 (corrected) tested the sharpest version of the conditioning idea: switch **execution mode** per
cell using the Scope A T4 drift gradient directly. On cells where the favorite leg drifts **up** by ≥X¢
(so a resting below-anchor maker bid will likely be swept *past*, not filled cheaply), **cross immediately
as a marketable taker** to lock entry; elsewhere keep the maker-wait. Paired-leg inverse logic; **net of
the 1¢ taker fee** on every crossed entry. Drift was read from the data and reproduced Scope A T4 within
**0.19¢** (gate ✓).

The drift-≥X trigger fires on **8 cells**, all heavy-favorite (r75_84 / r85_94). Sweeping the threshold:

| drift threshold | gross ROI | **net ROI** | net PnL | immediate-cross frac | fee |
|-----------------|-----------|-------------|---------|----------------------|-----|
| v3 baseline (maker-wait everywhere) | 12.105% | **10.514%** | $7,034.30 | — | — |
| ≥3¢ | 11.827% | 10.167% | $6,777.20 | 16.2% | $1,106.0 |
| **≥4¢ (best net)** | 11.919% | **10.266%** | $6,843.20 | 12.3% | $1,101.9 |
| ≥5¢ | 11.919% | 10.266% | $6,843.20 | 12.3% | $1,101.9 |
| ≥6¢ | 11.919% | 10.266% | $6,843.20 | 12.3% | $1,101.9 |

**Best threshold (≥4¢) nets 10.266% vs v3's 10.514% = −0.248pp. Every threshold is net-negative.** The
cross-taker mode does buy a cheaper entry on the cohort it touches — mean entry 75.84¢ vs v3's 76.82¢ on
the same cells, ~1¢ better — but (a) that ~1¢ is eaten by the 1¢ taker fee, and (b) on triggered-exit
events the cheaper entry doesn't flow to the realized +X anyway. The 8 favorite cells contribute **−$191.1**
net. Per-cell dominance 29/36, but corpus-net it loses. **Negative — not promoted to policy.**

(The original binary Phase 3 — a fixed 55¢ cross-favorites cutoff — found the cross-mode favorite entry
at 67.3¢ ≈ v3's 67.4¢, i.e. no improvement; that version is held unpromoted and superseded by this
corrected per-cell drift-driven version.)

---

## Section 5 — The contrast: Path B v4 IS positive (+1.02pp) on the static-offset lever

The same week, Path B v4 (ROADMAP T47, commit `c90985b`) asked a different question of the *same* atlas
exit and *same* corpus: not "condition the offset on per-event features" but "**re-optimize the static
per-cell offset on the deployment-correct objective**." v1 chose offsets to maximize entry-capture
(`fill_rate × offset`); v4 re-swept the (placement × offset) grid maximizing **net realized PnL through
the full strategy** (entry capture + atlas X exit + miss-fallback − 1¢ fee).

| Metric | v4 | v3 | atlas baseline |
|--------|-----|-----|----------------|
| Net PnL @10ct | **$7,765.70** | $7,116.70 | ~$5,094 |
| Capital | $66,231 | $66,506 | $70,813 |
| **Blended net ROI** | **11.73%** | 10.70% | ~7.2% |

**+1.024pp, gate-6 material, on lower capital → deployable** (`per_regime_offsets_v2.csv`, policy v4
Section 12). The load-bearing change: v4's offsets are **shallow** — 27/36 cells want 1–3¢, the opposite
of v1's deep "15¢-for-favorites." 34/36 cells re-optimize away from v3; 25 show material gain.

The juxtaposition is the whole point: **per-event conditioning of the offset (Path C) yields nothing; a
static re-setting of the same offset (Path B v4) yields +1pp.** Same exit, same features available — the
value was never in the per-event variation, it was in the level, which v1 had set against the wrong
objective.

---

## Section 6 — The unified mechanism: a fixed-profit exit caps entry-side conditioning

All three Path C negatives and the one Path B v4 positive reduce to a single structural fact:

> **The locked atlas exit realizes a fixed +X cents above entry, independent of entry price, whenever the
> +X target is hit (the majority outcome on most cells). The entry discount therefore does NOT flow into
> the dominant payoff — it only changes the hold-to-settlement minority (where realized PnL is `99−entry`
> / `−(entry−1)`, entry-dependent) and the deployed capital.**

Consequences, in order:

1. **Skip-gating (Phase 1) loses** because v3's miss-fallback is a costless taker-at-anchor; skipping
   low-P events removes cheap fills without any compensating gain (LESSONS A42).
2. **Offset modulation (Phase 2) is noise** because confidence-weighting the offset reshuffles entry
   prices, but the entry price barely matters once the exit caps the payoff at +X.
3. **Execution-mode switching (Phase 3) is net-negative** because crossing to lock a ~1¢-cheaper entry
   costs a 1¢ fee, and the ~1¢ doesn't reach the realized +X anyway.
4. **Static offset re-optimization (v4) wins** because it is not trying to capture more on the *exit* — it
   minimizes *miss rate* (deep offsets miss → fallback to the higher anchor = zero improvement) and
   *capital*, by setting a shallow offset that fills reliably at a small consistent discount and reduces
   deployed capital. It moves the two levers the exit cap leaves open (fill rate, capital), not the one it
   closes (per-fill capture).

A working fill predictor cannot beat this because **the thing it predicts — whether/how a below-anchor
bid fills — only governs the entry price, and the entry price is the variable the fixed-profit exit makes
irrelevant on the majority outcome.** The predictor is real (Section 2); the architecture just has no
entry-side channel to spend it on.

---

## Section 7 — Future work

Path C closes the *entry-side feature-conditioning* question as a structural negative. The channels it
does **not** foreclose, in rough priority:

- **Exit-side conditioning.** The cap exists because the exit (+X) is locked and uniform per cell. A
  predictor for *exit* outcomes — e.g. which events will spike past +X vs stall, or per-event hold-vs-exit
  — attacks the binding constraint directly rather than the capped entry side. This is the natural
  successor and the only Path-C-style idea with a credible mechanism to beat v4.
- **Re-optimize the exit X per cell on net-PnL** (the v4 move, applied to the exit lever instead of the
  offset). The atlas X's were fit on a hindsight-optimal exit-or-hold rule, not on the full
  entry+exit+fee strategy objective; there may be headroom analogous to v4's.
- **Layer B v2 tick-level fill realism** (T36, not built) — replace the minute-cadence fill simulator;
  required before any of the above ROI numbers can be trusted past the B25 discount.
- **The strategy work is otherwise CLOSED.** The deployable spec is bid_laying_policy v4 + v2 offsets;
  remaining work is execution-lock, not strategy: Bug 4 settlement mechanics → Layer B v2 → paper-mode
  integration → live.

---

## Section 8 — Realism caveats

- **Pre-realism throughout.** B25's 0.5–0.7× discount applies to every figure; the Phase 2 +0.08pp gross
  does not survive it (it is already inside the noise band), and v4's +1.02pp deploys at ~+0.5–0.7pp.
- **Phase 1 generalization is unproven.** Holdout AUC (0.73, Mar–May 2026) exceeds CPCV (0.66); both clear
  0.62, but the gap suggests the recent window is more drift-predictable. `taker_imbalance` rests on sparse
  pre-T-4h flow (61% data-available).
- **The negatives are robust to the optimism.** Phase 1's skip-rules and Phase 2's modulation use the
  holdout-trained P applied to all N (in-sample-optimistic for CPCV rows) — yet they still underperform,
  so the conclusion strengthens, not weakens, out of sample.
- **Fee model:** flat 1¢ taker on marketable_taker + miss_fallback; 0 on maker_resting (conservative).
  Phase 3's net figures carry this fee; Phase 1/2's gross figures do not (and the modulation gain is
  pre-fee, so net it is worse).
- **Per-cell optima are corpus-hindsight at the cell level**, but each cell's choice is observable a priori
  from the anchor regime (not per-event foresight), so v4 is deployable; Path C's per-event conditioning
  would have required deploy-time prediction, an additional unproven step that the negative result makes
  moot.

---

## Provenance

| Phase | Producer | Outputs (on-disk only) | Result |
|-------|----------|------------------------|--------|
| C-1 predictor | `build_path_c_phase1.py` (`22f3221`) | — (committed earlier) | predictor valid, AUC 0.73; skip-gates −2.8pp |
| C-2 offset modulation | `build_path_c_phase2.py` | `path_c_phase2_per_n_simulation`, `path_c_phase2_per_regime_summary` | **negative** (+0.08pp gross) |
| C-3 execution mode (corrected) | `build_path_c_phase3_corrected.py` | `path_c_phase3_corrected_per_n_simulation`, `path_c_phase3_corrected_per_regime_summary` | **negative** (−0.24pp net) |
| B v4 (contrast) | `build_path_b_v4.py` (`c90985b`) | `path_b_v4_per_n_simulation`, `path_b_v4_cell_optimum` | **positive** (+1.02pp net) — DEPLOYED |

Related: LESSONS A42 (skip-gating fails when fallback is safe), A43 (the fixed-profit-exit cap). Policy:
`docs/bid_laying_policy_v1.md` v4 (Section 12). Predecessor analyses T46 (Path B v1–v3), T47 (Path B v4).
