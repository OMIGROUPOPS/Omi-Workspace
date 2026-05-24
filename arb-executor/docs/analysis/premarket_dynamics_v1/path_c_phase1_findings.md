# Path C Phase 1 — 3-feature drift predictor (Plex Round 7 priority Tier 1)

**Date:** 2026-05-23
**Universe:** atlas — 14,033 N. **Target:** `drift_reached_bid` (did min(ask, last-traded) over T-4h→T-20m
reach the per-regime target bid). **Features at T-4h:** initial_spread, taker_imbalance_30min,
paired_arb_gap. **Pre-realism.** Implements Plex Round 7 (`9d11ed9`) Tier-1 "concrete corpus-testable
starting point" — does conditional placement help?

## Sources (read-only)

| Artifact | sha256 / note |
|----------|---------------|
| `premarket_tape_v1.parquet` | `ff2a63d9…` — features 1 & 3, drift target ([20,240]) |
| `per_minute_features.parquet` | `9fde4b5d…` — feature 2 taker window ([240,270], pre-T-4h) |
| `path_b_v3_per_n_simulation.parquet` | per-N realized PnL for the conditional-rule comparison |
| `docs/policy/per_regime_offsets_v1.csv` | per-regime target-bid offsets |

**Substrate / method notes.** Feature 2 (taker imbalance over the 30 min *before* placement, ttm
[240,270]) is sourced from `per_minute_features` — `premarket_tape_v1` is filtered to [20,240] and has
no pre-T-4h data; the before-window is causally correct for a T-240 predictor (Plex's "T-4h→T-3.5h"
after-window would be look-ahead). No sklearn on the VPS → AUC (rank-based), logistic regression
(IRLS/Newton, SEs from inverse Hessian), CPCV folding, and SFI/permutation importance are implemented
in pure numpy. `taker_data_available` = 61.1% (premarket taker flow is sparse pre-T-4h).

## Section 1 — Feature distribution

All three features have variance in **36/36** (category × regime) cells (gate 2 ✓). `drift_reached_bid`
= **3,983** of 14,033 (28.4%) — **exactly** Path B v3's fill count (gate 3 ✓).

## Section 2 — Univariate (SFI)

| Feature | corpus AUC | mean per-cell AUC | cells with AUC>0.60 |
|---------|-----------|-------------------|---------------------|
| paired_arb_gap_cents | 0.616 | 0.613 | **20** |
| initial_spread_cents | 0.597 | 0.592 | **19** |
| taker_imbalance_30min (\|·\|) | 0.433 | 0.423 | 0 |

`paired_arb_gap` is the standout single feature. Within-cell lift is large where it has signal — e.g.
**ATP_MAIN r45_54: base fill 12.3% → conditional (gap≥5¢) 40.0%, lift 3.24×, AUC 0.746**; r55_64
11.6%→35.3% (3.03×); favorite r75_84 31.6%→73.5% (AUC 0.747). A ≥5¢ paired gap at T-4h roughly triples
the fill probability — a directly deployable, B23-grounded signal. `initial_spread` is a weaker but real
second signal (19 cells >0.60). `taker_imbalance`'s univariate magnitude-AUC is <0.5 (its signal is
*signed*, captured in the multivariate model below — see §3).

## Section 3 — Multivariate logistic (CPCV + holdout)

- **CPCV (28 paths, 8 folds k=2, year-week tournament blocks, 2-week embargo): mean AUC 0.6625 ± 0.0418.**
- **Holdout (Mar–May 2026, 6,047 events never in CPCV): AUC 0.7298 — clears the 0.62 bar (gate 4 ✓).**

Standardized coefficients (holdout-trained model, regime fixed effects; all 95% CIs exclude 0):

| Feature | coef | 95% CI | odds ratio | permutation importance (AUC drop) |
|---------|------|--------|-----------|-----------------------------------|
| paired_arb_gap_cents | +0.155 | [0.077, 0.233] | 1.168 | 0.0038 |
| initial_spread_cents | +0.116 | [0.038, 0.193] | 1.123 | 0.0033 |
| taker_imbalance_30min | **−0.218** | [−0.270, −0.165] | 0.804 | **0.0220** |

**taker_imbalance dominates the holdout AUC (permutation 0.022, ~6× the others)** — as Plex predicted it
would dominate, but with a **negative** sign: more net *buying* at T-4h → *lower* probability of reaching
a below-anchor bid, which is mechanically coherent (taker buying pushes price *up*, away from a bid set
below the anchor). paired_arb_gap and spread contribute positive, significant, but smaller marginal lift
(their signal is partly absorbed by the regime fixed effects and by each other).

## Section 4 — Conditional fill-rate / ROI estimate

Two gates tested against Path B v3 (place-everywhere, 12.11% blended ROI; reproduced exactly here):

| Rule | place fraction | blended ROI | vs v3 |
|------|----------------|-------------|-------|
| v3 baseline (place all) | 100% | 12.11% | — |
| Rule A — ≥2/3 thresholds | 7.1% | 9.17% | **−2.94pp** |
| Rule B — P(drift)>0.5 | 20.6% | 9.36% | **−2.75pp** |

**Both binary gates LOWER ROI than place-everywhere.** This is the decisive, slightly counterintuitive
finding: because v3 already falls back to a costless taker-at-anchor on misses, *skipping* placement on
low-P events forgoes the cheaper fills those events would sometimes have gotten, with no offsetting gain
— it just reduces volume. A fill predictor's value is therefore **not** in a binary place/skip gate; it
is in **offset modulation** (place more aggressively — larger offset — when P(drift) is high; conservative
when low), which Phase 2 must implement. (Note: the rule comparison uses the holdout-trained model's
P applied to all N, in-sample-optimistic for the CPCV rows — yet the rules still underperform, so the
skip-gating conclusion is robust.)

## Section 5 — Recommendation

**Build Path C Phase 2 — but as offset modulation, not skip-gating.** The 3-feature predictor has real
out-of-sample signal (holdout AUC **0.73**, well above the 0.62 bar; paired_arb_gap and taker_imbalance
both significant and mechanically coherent). The single strongest deployable feature is the **paired
arb gap at T-4h** (within-cell fill-rate lift up to 3.5×). Phase 2 should map P(drift_reached_bid) →
bid aggressiveness (offset size), since the Phase 1 binary skip-rules show that gating placement on/off
cannot beat unconditional placement when the fallback is safe. If Phase 2's modulated-offset simulation
does not beat v3's +3.41pp, the conclusion is that the +3.41pp Path B ceiling is close to what this
feature set can extract and the conditional refinement is marginal.

## Section 6 — Realism caveats

Pre-realism (B25 0.5–0.7× not applied to any conditional rule). `taker_imbalance` rests on sparse
premarket flow (61% data-available) sourced from the pre-T-4h window of per_minute_features. The holdout
(43% of corpus, Mar–May 2026) shows higher AUC (0.73) than CPCV (0.66) — both clear 0.62, but the gap
suggests the recent window is more drift-predictable; deploy-time generalization is still unproven.
`pred_p_drift` in the outputs is from the holdout-trained model applied to all N (in-sample for CPCV
rows — use the CPCV/holdout AUCs, not in-sample fit, for the signal-strength claim). The conditional-rule
ROIs are pre-realism and assume v3's fill mechanics.

## Validation gates

1. Row count 14,033. ✓
2. Feature non-degeneracy: all 3 features vary in 36/36 cells. ✓
3. drift_reached_bid 3,983 == Path B v3 fill count (exact). ✓
4. Holdout AUC 0.7298 > 0.62. ✓
5. Conditional rules: both LOWER ROI than v3 (Rule A 9.17%, Rule B 9.36% vs 12.11%) — documented tradeoff: binary skip-gating reduces volume without increasing per-fill capture; the signal's value is offset modulation (Phase 2), not skip-gating. (Documented, not a STOP.)
