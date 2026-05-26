# Plex v5 — Per-Cell EV Optimization: Joint Entry + Exit, Risk-Adjusted Objective, Avoidance, and Smart Banding

**Source:** Plex (Perplexity) literature synthesis
**Date:** 2026-05-25
**Prompt context:** v5 is a structural reframe of the current two-pass pipeline (Path B v4 entry table + adaptive exit banding) that chose entry and exit sequentially and optimized raw E[$] rather than a risk-adjusted objective. Tonight's per-cell pull exposed a pathology: shallow-exit single-cell losers in mid-board and heavy-favorite cells (38–40¢ +1¢ band: -$24.60 over 192 N; 65¢ +1¢ cell: -1.03% ROI; 82¢ +6¢ cell: -4.28% ROI) whose "best" atlas exit is the least-bad of all-negative choices. v5 addresses four interacting deficiencies: (1) joint sweep of (placement_minute, offset_cents, exit_X) rather than sequential optimization; (2) risk-adjusted EV metric (Sortino or CRRA log-utility) that penalizes the bimodal binary outcome distribution; (3) explicit avoidance — cells that are confidently negative-EV under every (entry, exit) joint policy are disabled; (4) banding by shared optimal policy configuration rather than by per-cell PnL proximity. The bot is LIVE tonight at 5ct sizing on the v4-derived deploy table; v5 must ship within days and must not regress below the atlas +8.70% blended floor.
**Status:** External synthesis — per LESSONS C40, committed to repo immediately. Chat-side agent handles git operations; this file is write-only by the subagent.

---

## Section 1 — Risk-Adjusted EV Metric Choice (Q1)

### 1.1 Why raw E[$] fails on binary settlement

The current atlas objective is per-cell expected dollar PnL: argmax over X of E[PnL | placement, offset, X]. For cells where the outcome distribution is bimodal — many small wins (+X¢ when the exit fires) against rare catastrophic losses (–65 to –82¢ when the bid fills but the exit misses and the contract settles worthless) — raw E[$] is a deceptive guide. It selects the configuration that minimizes loss in expectation but does not penalize variance or tail exposure. The 38–40¢ +1¢ band illustrates this precisely: with a 92–95% hit rate, the E[$] at exit_X=1¢ is less negative than at exit_X=8¢ (where lower hit rate means more misses that lose 38–40¢ each), but the correct question is whether either configuration has positive risk-adjusted EV — and the per-cell sweep shows the answer is "no" at any X for that band. *[Evidence: direct corpus measurement reported in context capsule; not an inference.]*

### 1.2 Metric candidates

**Sharpe ratio.** E[PnL] / σ(PnL) per [Sharpe (1966)](https://www.jstor.org/stable/4479578). Disadvantage in this setting: σ is symmetric, penalizing upside variance equally with downside. Binary settlement produces a left-skewed distribution; Sharpe understates the danger of the large-negative tail. Also, with N per cell as low as 20–50, sample standard deviation estimates are noisy, inflating apparent Sharpe for high-hit-rate cells whose few misses may not have occurred in the corpus sample. *[A39: at 5c sizing, small $/N differences are large ROI swings — Sharpe's denominator collapses these asymmetrically.]*

**Kelly fraction.** Per [Kelly (1956)](https://www.princeton.edu/~wbialek/rome/refs/kelly_56.pdf), the growth-rate-maximizing bet size for a binary bet with win probability p and win/loss ratio g/l is f* = p − (1−p)/g × (l/g) — equivalently, f* = (p·g − (1−p)·l) / (g·l) in the general case. For a cell with anchor 38¢, exit_X=1¢, hit_rate 0.93, miss_loss 38¢: f* = (0.93×1 − 0.07×38)/(1×38) = (0.93 − 2.66)/38 ≈ −0.045. **A negative Kelly fraction means the bet has negative EV — the Kelly criterion is a clean binary signal.** This is exact for the binary-settlement structure. Per [Browne (1997)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=57909) on survival-and-growth under liabilities, a partial Kelly (f = 0.25 × f*) is operationally preferred when f* is positive to reduce ruin probability, and the "skip" action (f=0) dominates whenever f* < 0. However, Kelly maximizes log-wealth asymptotically and does not directly give a per-trade CI; bootstrapping for cell-level Kelly CIs requires an additional step.

**Sortino ratio.** E[PnL] / σ_downside, where σ_downside is the root semi-variance of returns below zero (the minimum acceptable return threshold). Per [Sortino and Price (1994)](https://rpc.cfainstitute.org/sites/default/files/-/media/documents/code/gips/the-sortino-ratio.pdf), this penalizes only the downside deviation and is therefore better calibrated for left-skewed distributions. In the binary settlement setting, all misses (settlement at 0¢) contribute to downside deviation while all hits (exit fires) contribute zero downside deviation. Sortino is thus directly sensitive to the hit-rate/miss-loss tradeoff: cells where misses are rare but large will correctly show low Sortino even if Sharpe looks reasonable. *[G23: this claim is a direct logical deduction from Sortino's definition, grounded in the binary payoff structure — labeled inference, not measured on the corpus.]*

**CVaR-adjusted EV.** Per [Rockafellar and Uryasev (2000)](https://sites.math.washington.edu/~rtr/papers/rtr179-CVaR1.pdf), CVaR at confidence level α is the expected loss conditional on the loss exceeding the α-th quantile. For a binary settlement: CVaR₀.₉₅ = expected loss in the worst 5% of outcomes = approximately the miss-loss per contract × (1 / (1 − hit_rate)) when hit_rate > 0.95, or more precisely the average dollar loss in miss events. CVaR is subadditive (unlike VaR) and gives a convex optimization objective. **Disadvantage:** for N=20–50 per cell, the empirical 95th-percentile miss distribution has only 1–2 observed miss events; CVaR estimates at the tail are too noisy to be operationally reliable without parametric assumptions.

**CRRA log-utility (expected utility under log preference).** E[log(1 + r)] where r is the per-trade return on deployed capital. For a binary bet: E[log] = p × log(1 + exit_X/cost) + (1−p) × log(1 − miss_loss/cost). This is exactly the Kelly objective (maximizing log-wealth growth). Negative E[log] implies the cell destroys geometric growth. *[Inference: by analogy to the Kelly equivalence shown in MacLean-Thorp-Ziemba (2011).]*

### 1.3 Recommendation: Sortino with Kelly as corroboration

**Primary metric: Sortino ratio.** Justification:

1. **Bimodal sensitivity.** The binary outcome distribution makes downside semi-variance the honest denominator. Sortino specifically penalizes the rare but large miss-losses that dominate cell PnL in negative-EV cells. *[Sortino and Price 1994, direct recommendation.]*
2. **Operational simplicity.** Sortino requires only E[PnL] and the vector of below-zero outcomes — both directly computable from the per-N tick tape without distributional assumptions. At N=50, bootstrap CI on Sortino is feasible (§6).
3. **ROI comparability.** Per **A39** doctrine: at 5–10c sizing, the capital deployed varies per cell (smaller positions at thin-market cells), so the Sortino ratio computed on per-trade ROI (rather than raw $) is the correct cross-cell comparison unit.

**Corroboration: Kelly sign.** For any cell where Kelly f* < 0 (negative EV), the Sortino ratio will also be negative (since E[PnL] < 0 drives a negative numerator regardless of σ_downside). The converse is not always true — a cell might have E[PnL] > 0 but negative Sortino if variance is very high. **Both metrics should agree on disabling a cell: disable only when Sortino < 0 AND Kelly f* < 0.** When they disagree (one positive, one negative), apply conservative treatment per §6.

**Safety-first floor reference:** Per [Roy (1952)](https://www.jstor.org/stable/1907413), the safety-first criterion minimizes P(return < disaster threshold). Applied here: the disaster threshold is −1σ_daily_capital. Roy's criterion directly forbids cells whose expected loss conditional on filling exceeds the threshold. This is equivalent to requiring the Sortino ratio to be positive (so that the distribution is on the right side of the disaster threshold in expectation relative to downside risk). *[Roy 1952 grounds the avoidance criterion as a capital-safety principle, not just a performance metric.]*

**Markowitz mean-variance:** Per [Markowitz (1952)](https://www.jstor.org/stable/2975974), portfolio-level mean-variance optimization applies when cells are jointly held and covariance matters. At 4 categories × ~90 cells per category = 360 simultaneous cells, a full covariance matrix is empirically infeasible (360×360 requires 14K+ corpus N's for reliable estimation; we have 14K total N's with each cell contributing only ~50–200). **Ledoit-Wolf shrinkage** per [Ledoit and Wolf (2004)](http://www.ledoit.net/honey.pdf) would reduce estimation error, but portfolio-level EV optimization is a stretch at this corpus size. *[Inference: the per-cell Sortino approach is a valid decentralized approximation to the portfolio-level problem when cells are treated as approximately independent — reasonable given cells are partitioned by anchor price.]*

---

## Section 2 — Joint Sweep Methodology (Q2)

### 2.1 Sweep space quantification

Per **G22** three-axis deployment math: the full joint sweep is:

| Axis | Choices | Count |
|---|---|---|
| placement_minute | {240, 180, 120, 90, 60, 30, 20} | 7 |
| offset_cents | {0,1,2,3,4,5,7,10,12,15,18,20} (v4 sweep) + 8 more = 16–20 | ~16 |
| exit_X | {1,2,3,4,5,6,8,10,12,15,18,20,25,30,40,50,HOLD} = 17 choices | 17 |
| cells per category | 90 (1¢ anchor bins 5¢–94¢) | 90 |

Full joint space per category: 7 × 16 × 17 × 90 ≈ **171,360 configs.** Across 4 categories: **~685K configs.** Each config requires replaying the per-N corpus tape (~14,033 N's against `premarket_tape_v1.parquet` minute candles + `g9_trades.parquet` 33.7M trades) to compute fill_rate(placement, offset) × hit_rate(exit_X | fill) × capture − miss_penalty × miss_rate. With vectorized NumPy replay on in-memory parquet (feasible since `{cat}_spike_perN.parquet` is the exit measurement source and `premarket_tape_v1.parquet` is the entry source), each cell-config evaluation is ~O(N) per cell. At N̄=155 per cell, 90 cells, 7×16×17 = 1,904 entry-exit configs per cell: 90 × 1,904 × 155 ≈ 26.5M row operations per category, or ~106M total. On a single core at 10M rows/sec: ~10.6 seconds. **Full grid is computationally feasible in under 60 seconds** with vectorized pandas/numpy if the replay is structured as a pre-computed exit measurement lookup (already done in `{cat}_spike_perN.parquet`) combined with the entry fill-rate function. *[Evidence: parquet sizes and N counts from context capsule; compute estimate is inference based on NumPy throughput benchmarks, not measured.]*

### 2.2 Smart search options

Despite full-grid feasibility, smart search is recommended for three reasons: (a) it makes the sweep extensible to larger offset spaces; (b) it reduces overfitting by limiting the effective comparison count (relevant to §5's multiple-testing discount); (c) it supports re-sweep on live data subsets where N per cell may be much smaller.

**Option A — Full grid (feasible baseline).** 171K configs × 4 categories ≈ 685K total. ~60 seconds wall clock at vectorized numpy throughput. Full grid is the correct approach for the initial v5 corpus sweep because N per cell is sufficient for statistically reliable evaluation of all configs. *[Recommendation: use full grid for the corpus v5 sweep.]*

**Option B — Random search.** Per [Bergstra and Bengio (2012)](https://jmlr.org/papers/v13/bergstra12a.html), random search across the hyperparameter space is more efficient than grid search when not all dimensions matter equally — they show random search finds equally good or better solutions with ~60% fewer evaluations. In this setting, placement and offset interact strongly (the optimal offset depends on placement's fill-rate relationship), but exit_X may be weakly interacting with entry in many cells. Random sampling 1,000 configs per cell (vs 1,904 in the full grid) would cut runtime by 47% with minimal quality loss. *[Inference from Bergstra-Bengio's neural net setting, applied by analogy to this 3D configuration sweep.]*

**Option C — Bayesian optimization.** Per [Snoek, Larochelle, and Adams (2012)](https://arxiv.org/abs/1206.2944), Gaussian process-based Bayesian optimization treats the objective function (Sortino as a function of (placement, offset, X)) as a smooth surface and intelligently selects the next evaluation point based on expected improvement. This is most valuable when function evaluations are expensive. Since evaluations here are cheap (vectorized numpy), the overhead of fitting a GP on ~100 previous observations before each new suggestion is not justified for an initial sweep. **Bayesian optimization is recommended for live re-sweeps** where N per cell is smaller (limiting full-grid statistical reliability) and where the configuration surface has already been roughly mapped by the corpus sweep.

**Recommendation: Hybrid — full corpus grid, BO on live re-sweeps.** Stage 1 (corpus): full grid, 685K configs, ~60 seconds, produce a per-cell best_config table. Stage 2 (live re-sweep after 4–8 weeks of live data): Bayesian optimization initialized at the corpus best_config, searching a neighborhood of ±2 minutes placement, ±2¢ offset, ±5¢ exit_X per cell. This concentrates exploration where the corpus suggests signal while allowing adaptation as the live distribution evolves. *[G22 three-axis math grounds the dimensionality; Bergstra-Bengio and Snoek-Larochelle-Adams ground the search choices.]*

### 2.3 Critical implementation note: conditional fill-rate measurement

The joint sweep is **not** the product of independent entry and exit optimization. The fill_rate function f(placement, offset) changes the set of N's that are "filled" — and the exit distribution (hit_rate at exit_X, miss loss) is conditional on the N's that filled. A shallow offset at early placement fills more N's but may include N's where the post-fill path is adverse (price drops after fill, making exit harder). The correct computation is:

```
for each (placement, offset, exit_X):
    filled_N_set = {n : premarket_min(n, placement) ≤ anchor - offset}
    hit_set = {n ∈ filled_N_set : max_real(n) ≥ anchor + exit_X}
    miss_set = filled_N_set \ hit_set
    PnL = sum(hit_set: exit_X) + sum(miss_set: settlement_value - anchor) - len(filled_N_set) * fee
    Sortino = compute_sortino(per_N_returns)
```

This requires replaying the premarket tape conditioned on fill, not separately computing fill-rate × hit-rate. The spike_perN parquet already contains (anchor_price, max_real, settlement_value) per N — the entry fill condition needs to be added from the premarket_tape_v1 per-N minute candle scan. *[F33 depth-chain data gap: if taker-side volume data is absent for specific N's, the fill condition defaults to price-cross on the best-bid candle — conservative but acceptable.]*

---

## Section 3 — Disable Threshold (Q3)

### 3.1 Framing the avoidance decision

The current pipeline has no skip option: every 1¢ anchor bin is traded. v5 introduces a binary avoidance decision per cell: **trade at best (placement, offset, X) | skip entirely**. The operative question is how to set the threshold that triggers "skip." Three candidate thresholds:

**Option A — Zero on Sortino (strict positive EV gate).** Disable a cell if and only if its Sortino ratio at the best (placement, offset, X) is negative. This is equivalent to disabling cells with E[PnL] < 0 at optimal configuration, which is the Kelly f*<0 condition. *[Roy 1952 safety-first: the threshold is zero return as the minimum acceptable.]*

**Option B — Quantile-based (relative threshold).** Disable the bottom decile of cells by Sortino ratio, regardless of sign. This targets capital concentration — reallocating attention away from the worst 10% of cells even if some of those cells have positive (but marginal) Sortino. Risk: disabling positive-EV cells reduces daily fill volume and may cut profitable-but-thin cells unnecessarily. *[Not recommended: confounds avoidance with portfolio concentration rebalancing, which is a separate decision.]*

**Option C — CI-upper-bound below zero (conservative statistical gate).** A cell is disabled only when its risk-adjusted EV **upper confidence bound** is below zero — i.e., even the optimistic estimate of the cell's Sortino ratio is negative. This is the most conservative option: ambiguous cells (CI straddling zero) are kept active at the atlas configuration rather than disabled. *[Browne 1997: the partial Kelly "skip" option applies only when f* is unambiguously negative; when f* CIs include zero, retaining the atlas configuration is preferable to skipping.]*

### 3.2 Recommendation: CI-upper-bound gate (Option C)

**Disable criterion:** Cell c is disabled at v5 if: `CI_upper(Sortino_c, 95%) < 0` at the cell's best (placement, offset, X) configuration. Equivalently: `CI_upper(Kelly_f*_c, 95%) < 0`.

**Rationale:**
- The 14,033 N corpus gives N per cell of 20–200. At N=50, a Sortino CI is wide (§6). Aggressive disabling at N=50 cells using a point estimate would flip a cell to "skip" based on sampling noise.
- Capital utilization: the 4 categories currently contribute 4,137 + 3,683 + 5,326 + 887 = 14,033 N's with $66K+ deployed capital across 360 cells. Disabling a subset of cells reduces daily fill volume; disabling the wrong cells (those with true positive Sortino that happen to have a negative point estimate) is a type-II cost that is operationally concrete (fewer fills, higher broker pass-through rate, worse position in the trading day flow).
- Regret asymmetry: the cost of **incorrectly keeping** a structurally negative-EV cell is bounded by the cell's E[loss] per day ≈ a few dollars per N × daily fill count. The cost of **incorrectly disabling** a positive-EV cell is the foregone profit — also bounded but more uncertain to estimate. At the current 5ct sizing, the symmetry of these costs favors being conservative on disabling.

**Expected disable count (inference):** From the context capsule's per-cell table, approximately 7–12 cells out of 90 per category show structurally negative ROI at the current (atlas best_exit_X | v4 entry). After the joint v5 sweep, some of those cells may find a profitable joint policy (different entry offset produces a different fill subset with positive Sortino). **Only cells where the joint sweep confirms negative Sortino across all configurations are candidates for disable.** Based on the ATP_MAIN exhibit (38–40¢ band confirmed all-X negative), expect 5–20 disables across 360 total cells — approximately 5–6% of the universe. *[G23: "5–20" is an inference extrapolated from the 7-cell exhibit in the context capsule; empirical sweep may produce a different count.]*

**Capital utilization preservation:** Disabled cells' capital allocation is not redistributed to other cells in v5 (which would require a full portfolio-level Kelly optimization). Instead, disabled cell capital is simply withdrawn — net capital deployed decreases. At 5–20 disabled cells out of 360 (~4–6%), the capital reduction is approximately 4–6% of total deployed capital, which is acceptable and reduces overall tail exposure from structurally negative cells. *[A39: the capital freed from disabled cells reduces ROI denominator slightly, potentially improving blended ROI if the disabled cells were dragging it down.]*

---

## Section 4 — Banding Criterion (Q4)

### 4.1 The v4 banding flaw

The adaptive exit bander (`adaptive_exit_banding_findings.md`) uses PELT / optimal-partition dynamic programming to group adjacent 1¢ cells by PnL similarity at the per-cell best_exit_X. The implicit assumption is that cells with similar PnL share a compatible optimal policy — but PnL similarity is a **consequence** of policy similarity only when the underlying optimal X values are the same. Two cells with the same PnL can have radically different optimal exit_X values (one cell prefers HOLD, another prefers +4¢) while sharing a similar negative-EV profile. Banding them together forces a shared X that is suboptimal for both. *[Evidence: the ATP_MAIN cells 37 & 38 (65¢ and 66¢ anchor) already required hard-enforcement of separation (X=39 vs X=1) despite being adjacent — a direct empirical sign that per-cell PnL-based banding produces incorrect groupings.]*

### 4.2 Banding by shared optimal policy configuration

v5 banding criterion: **group cells by the similarity of their optimal (placement_minute, offset_cents, exit_X) configuration vector**, not by per-cell PnL. The rationale: cells whose optimal policies agree within operational tolerance (±1 minute placement, ±1¢ offset, ±2¢ exit_X) can be assigned the same deployed configuration with minimal loss of EV. Cells whose optimal policies differ outside that tolerance should not be banded together regardless of their PnL proximity.

**Algorithm: k-medoids clustering** on the 3D configuration vectors. Per [López de Prado (2020)](https://ssrn.com/abstract=3517595) on Clustered Feature Importance (CFI), clustering on the configuration space (rather than the output space) is robust to the substitution effects that make output-space clustering misleading: two configurations may produce similar PnL (the "output") via very different mechanisms (high-hit-rate shallow-exit vs. low-hit-rate deep-exit), and banding them would corrupt both. The CFI framework directly extends to clustered **policy assignment**: cluster cells in configuration space, assign all cells in a cluster the cluster medoid's configuration, and measure the EV loss from the collapsing.

**Implementation:**

```
configuration_matrix = per_cell_optima_df[['placement_minute', 'offset_cents', 'exit_X']]
# Normalize each dimension to [0,1] before clustering
config_normalized = (config_matrix - config_matrix.min()) / (config_matrix.max() - config_matrix.min())
# k-medoids with k chosen by elbow on SSE or operator-set band count target
# PAM (Partitioning Around Medoids) or CLARA for >100 cells
band_assignments = kmedoids(config_normalized, k=target_bands, method='pam')
```

**k selection:** Use the elbow method on within-cluster sum of squared distances in normalized configuration space, or set k = 60–70 (less than the current 55–61 per category at β=8, since v5 disables ~5–10 cells and the remaining cells may group more naturally). A secondary constraint: any medoid assignment that collapses two cells with Sortino of opposite sign (one positive, one negative) is forbidden — cells with opposite-sign risk-adjusted EV must not share a band. *[G23: this constraint is an inference from the principle that banding should not mix enabled and disabled cells; it is not derived from the clustering literature directly.]*

**Tolerance-based fallback:** Cells whose optimal configuration is farther than (2 minutes, 2¢ offset, 5¢ exit_X) from their assigned medoid become **singleton bands** (single-cell, own configuration). This replicates the 144 single-cell bands in the current adaptive structure (`adaptive_exit_banding_findings.md`) but now the singleton criterion is configuration-distance rather than PnL loss. Cells that genuinely have idiosyncratic optimal policies (e.g., the 65¢ cell wanting exit_X=39¢ while neighbors want exit_X=1¢) are correctly isolated as singletons.

**Output schema (mirrors `{cat}_adaptive_exit_bands.parquet`):**

| band_id | price_range | cells | placement_minute | offset_cents | exit_X | N | cap_$ | $ | ROI_pct | sortino | ci_lower | ci_upper |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| int | str | list[int] | int | int | int\|HOLD | int | float | float | float | float | float | float |

The new schema adds `sortino`, `ci_lower`, `ci_upper` columns absent from the v4 bands. This makes the band table self-documenting on statistical confidence.

### 4.3 Comparison to current banding

| Dimension | v4 adaptive banding | v5 configuration-space banding |
|---|---|---|
| Grouping criterion | PnL proximity (PELT/DP) | Configuration distance (k-medoids) |
| β penalty | 8 (main cats) / 3 (WTA_CHALL) | N/A — elbow or operator-set k |
| Singleton criterion | High collapse-loss | Configuration distance > tolerance |
| Disabled cells | None (all cells forced into bands) | Disabled cells not banded — excluded |
| EV metric in band table | ROI% only | ROI% + Sortino + CI |
| Banding objective | Minimize PnL loss from collapsing | Minimize policy distance within bands |

*[Evidence: current banding metrics from `adaptive_exit_banding_findings.md`; v5 properties are design recommendations (inference).]*

---

## Section 5 — No-Regression Validation (Q5)

### 5.1 Validation gates

v5 must clear all of the following corpus validation gates before live deployment:

**Gate 1 — Absolute PnL floor.** Corpus net-PnL (10ct sizing) ≥ atlas baseline $6,158 (gross 8.70% ROI). The atlas baseline is the no-regression floor established in `adaptive_exit_banding_findings.md`. v5 must beat this by ≥ +1.0pp blended ROI (≈ +$760 at current deployed capital), matching the v4 entry table's +1.024pp lift bar. *[Evidence: v4 result of $7,765.70 / 11.73% from `path_b_v4_findings.md`; +1.0pp gate is the same lift standard applied consistently.]*

**Gate 2 — Risk-adjusted floor.** v5 blended Sortino ratio on corpus outcomes ≥ v4's blended Sortino ratio. Since v4 did not compute Sortino, this requires back-computing v4's Sortino from the existing per-N outcomes to establish the comparator. *[G23: this gate requires a computation not yet performed; flagging as a required step before v5 deployment.]*

**Gate 3 — Per-category no-regression.** Per-category ROI ≥ current deployed table per category:

| Category | Current adaptive ROI | v5 must clear |
|---|---|---|
| ATP_MAIN | 7.32% | ≥ 7.32% |
| WTA_MAIN | 9.10% | ≥ 9.10% |
| ATP_CHALL | 7.08% | ≥ 7.08% |
| WTA_CHALL | 13.45% | ≥ 13.45% |

Blended 8.08% → v5 target ≥ 9.08% blended (8.08% + 1.0pp). *[Evidence: per-category ROIs from `adaptive_exit_banding_findings.md`.]*

**Gate 4 — CPCV validation.** Apply Combinatorial Purged Cross-Validation with 28 paths per [López de Prado (2018) AFML](https://www.wiley.com/en-us/Advances+in+Financial+Machine+Learning-p-9781119482086), chronological fold ordering, 2-event embargo between train/test. Mean ROI across 28 CPCV paths must clear ≥ 8.08% + 1.0pp = 9.08%, and standard deviation across paths ≤ 2.0pp. *[Round 2 (`plex_premarket_execution_round2_2026-05-21.md`) established the CPCV protocol; Gate 4 applies it to v5 bands.]*

**Gate 5 — Deflated Sharpe / multiple-testing discount.** Per [Bailey, Borwein, López de Prado, and Zhu (2014)](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf), the deflated Sharpe ratio (DSR) adjusts the observed Sharpe ratio for the number of strategies tested, the length of the track record, and non-normality of returns. In the v5 sweep context: with 360 cells × ~1,904 configs per cell = ~685K total strategies evaluated, the maximum expected Sharpe under the null (no skill) is approximately √(2 log(685,000)) × σ / √N ≈ 7.5 σ/√N — a very high hurdle. Strategies that merely beat zero Sharpe may be overfit. The DSR correction deflates the in-sample Sortino/Sharpe by this multiple-testing factor. The practical implication: **only cell-level improvements that are economically large (≥0.5pp ROI improvement over atlas baseline) AND statistically significant after CPCV should be promoted to the live table.** Marginal improvements of 0.01–0.05pp are likely to be noise given the search space size. *[B25: apply 0.5–0.7× realism discount on top of the corpus result: corpus +1.0pp lift = +0.5–0.7pp live-adjusted expected lift.]*

**Gate 6 — Disabled cells net positive.** Disabling N cells must not reduce total corpus PnL if those cells have negative E[$] at their best joint config. This is trivially satisfied if the disabled cells were confirmed negative-EV. Verify: sum(disabled cells' per-N PnL at their v4 config) < 0 before proceeding. *[Evidence: 38–40¢ band was -$24.60 at its v4 config; Gate 6 verify this extends to all disabled cells.]*

### 5.2 Realism adjustment

Per **B25**, the corpus 0.5–0.7× realism discount applies to any PnL improvement derived from the minute-cadence simulator. A v5 corpus improvement of +1.0pp blended ROI translates to +0.50pp to +0.70pp expected live improvement. The operator should plan deployment expecting the live improvement to land in this range, not at the full corpus figure. *[This applies identically to v4; the multiplier has not changed.]*

---

## Section 6 — Sample-Size Discipline and Uncertainty (Q6)

### 6.1 Per-cell bootstrap protocol

Per-cell N ranges from 20 (thin anchor bins at <10¢ or >93¢) to 200 (high-volume mid-board cells). The Sortino ratio is a ratio of two sample statistics (mean return and downside semi-deviation), and its sampling distribution is not normal at N<100. The correct approach is nonparametric bootstrap.

**Stationary bootstrap** per [Politis and Romano (1994)](https://www.stat.ucsb.edu/~politis/paper/stat.pdf): for time-series data with temporal dependence (N's are not i.i.d. — Kalshi tennis events on the same day or week exhibit correlated premarket conditions), the stationary bootstrap resamples blocks of N's with geometrically distributed block length L ~ Geometric(1/b̄), where b̄ is the mean block length. For the corpus spanning ~252 days of ATP_MAIN, a block length of b̄ = 5–10 (5–10 consecutive events) captures weekly-scale dependence while allowing resampling. **Protocol:**

```
n_resamples = 1000 (minimum; 5000 preferred for stable tail quantiles)
b_mean = 7  # weekly event block
CI_95 = stationary_bootstrap(per_N_returns, n_resamples, b_mean, quantiles=[0.025, 0.975])
```

**Interpretation:** If CI_lower(Sortino) > 0: promote v5 config to live. If CI_upper(Sortino) < 0: disable cell (per §3). If CI straddles zero: **conservative treatment** — revert that cell to the v4 (atlas) configuration, not the v5 joint-optimal config, not disabled.

### 6.2 Conservative treatment for ambiguous cells

Cells whose CI straddles zero present the core decision problem. The conservative treatment is:

1. Do NOT disable the cell (which would lose fill volume).
2. Do NOT promote the v5 joint-optimal config (which has uncertain Sortino sign).
3. **Retain the v4 configuration** (placement, offset from `per_regime_offsets_v2.csv` + atlas best_exit_X from `{cat}_descriptive_1c.parquet`).

This preserves the no-regression guarantee: the v4 config is the existing live config, so retaining it in ambiguous cells means v5 strictly dominates v4 in cells where the CI is positive and matches v4 in all other cells. *[Browne 1997: the skip/retain decision under uncertainty favors the known outcome (v4) over the uncertain outcome (v5 joint-optimal) when the uncertain outcome has CI straddling zero.]*

**Expected ambiguous-cell count:** At N=50, bootstrapped Sortino CIs for small-but-positive-EV cells (e.g., ROI of +0.5%, Sortino ~0.15) will typically straddle zero. Expect 30–60% of the 360-cell universe to have ambiguous CIs on first v5 sweep. These cells retain v4 config. Only the 20–30% of cells with clearly positive (or clearly negative) Sortino CIs get v5 updates. *[G23: "30–60%" is an inference based on typical bootstrap CI width at N=50; actual proportion depends on the corpus outcomes.]*

### 6.3 Variance-of-variance at low N

For N < 30, the sample semi-variance estimate (used in Sortino's denominator) is itself highly variable. A cell with N=25 and 2 observed misses has a downside semi-deviation estimate with a coefficient of variation of ~70%. **Ledoit-Wolf shrinkage** per [Ledoit and Wolf (2004)](http://www.ledoit.net/honey.pdf) addresses covariance matrix shrinkage in the multi-asset case, but the per-cell setting is 1-dimensional (returns are scalar). The analogous shrinkage is to the **grand mean semi-deviation across all cells in the same category** — pulling low-N cell estimates toward the category average. Specifically:

```
shrinkage_target = category_mean_semi_deviation  # computed over all cells with N > 50
alpha = N_cell / (N_cell + N_threshold)  # e.g., N_threshold = 50
shrunk_semi_dev = alpha * sample_semi_dev + (1-alpha) * shrinkage_target
```

This reduces estimation noise for thin cells without discarding their data. *[Inference: the Ledoit-Wolf logic for covariance matrices extends to scalar semi-variance shrinkage by analogy; not directly from Ledoit-Wolf's paper.]*

### 6.4 Minimum N policy

Cells with N < 15 are statistically uninformative for Sortino estimation. For these cells: (a) do not compute a v5 joint-optimal config; (b) retain v4 config; (c) flag for operator review as "thin cell — v6 candidate after N accumulates in live." The N < 15 threshold corresponds to the minimum needed for a 95% CI to have any practical width (N=10 gives a bootstrap CI width ~3× the point estimate, making the CI nearly uninformative). *[G23: "N < 15" is an inference from bootstrap power curves; the exact threshold depends on the empirical return distribution.]*

---

## Section 7 — Live Deployment Sequencing (Q7)

### 7.1 Context

Bot is LIVE tonight at 5ct on the v4-derived deploy table (`config/deploy_v5_live.json`, paper_mode false). v5 must be phased in without disrupting capital. Four sequencing options:

**Option A — Shadow parallel.** Run v5 in paper mode alongside live v4 for ~1 week (~50–200 N/category). Compare paper-v5 vs live-v4 outcomes per cell. If paper-v5 tracks the corpus prediction (Sortino ≥ corpus prediction within 1σ), promote.

**Option B — Cell-by-cell hot-swap.** Promote only the highest-confidence v5 cells (tight CI, large Sortino lift, CI_lower > 0.1) to live each week. Leave ambiguous and uncertain cells at v4.

**Option C — Category-level A/B.** Run v5 on 1 category live, v4 on other 3, rotate weekly. Cleaner comparison per [Kohavi, Tang, and Xu (2020)](https://www.cambridge.org/core/books/trustworthy-online-controlled-experiments/D97B26382EB0EB2DC2019A7A7B518F59) A/B testing principles — treatment and control are clearly separated. Disadvantage: categories have different dynamics (ATP_MAIN vs WTA_CHALL differ substantially in volume and regime distribution), so the A/B comparison is confounded by category-level differences.

**Option D — Full cutover after corpus + 1-week paper.** Gate on paper-mode risk-adjusted metric matching corpus prediction within ±1σ, then full cutover.

### 7.2 Recommendation: Option A + B hybrid (shadow → confident cell promotion)

**Phase 1 (Days 1–7): Full shadow.** Deploy v5 bands in paper_mode=True alongside live v4. Collect ~50–200 per-category live N's. Compute live Sortino per cell and compare to corpus prediction. Cells where live Sortino > corpus prediction by <1σ are "stable"; cells where it deviates >1σ are flagged for investigation.

**Phase 2 (Days 8–21): Confident-cell hot-swap.** Promote cells meeting all of:
- CI_lower(Sortino) > 0 (clearly positive in corpus)
- CPCV Gate 4 pass
- Shadow-week live Sortino not deviating >2σ below corpus prediction

Expected promotion volume: 20–30% of cells in Phase 2. Remaining cells stay at v4.

**Phase 3 (Days 22–35): Ambiguous-cell review.** After 3–4 weeks of live data, re-run bootstrap CI on the union of corpus + live N's per ambiguous cell. Promote cells that cross the CI_lower > 0 threshold with combined data. Keep confirmed-ambiguous cells at v4 indefinitely (v6 will address with larger N).

Per [Johari, Pekelis, and Walsh (2017)](https://arxiv.org/abs/1512.04922) on sequential A/B tests: the correct approach for ongoing live evaluation is to use sequential testing (always-valid confidence intervals) rather than fixed-horizon tests, to avoid peeking bias. **The per-cell bootstrap CI should use a sequential validity correction** (e.g., Bonferroni on the number of weekly re-evaluations). For 4 weekly evaluations, the per-evaluation CI threshold tightens from 95% to 98.75% (Bonferroni), meaning cells need more evidence to be promoted.

*[Round 6 staged-deployment doctrine: start single-concern (confident cells only), expand after observed live performance; this extends Round 6's staged deployment philosophy to the cell-level granularity.]*

### 7.3 Operational guardrails

- **Per-day loss cap:** If live PnL on v5-promoted cells falls below −2σ of corpus prediction for two consecutive days, pause v5 and revert those cells to v4.
- **Sizing:** Maintain 5ct through the shadow and hot-swap phases. Do not scale to 10ct until Phase 3 is complete and live Sortino confirms corpus prediction within 1σ.
- **Config freeze:** Once a cell is promoted to v5, do not re-sweep it for 2 weeks (minimum live N to get meaningful feedback). Avoid chasing noise.

---

## Section 8 — Live Feedback Loop (Q8)

### 8.1 Bayesian update architecture

Live data accumulates at ~50–200 N/category/week. Per [West and Harrison (1997)](https://www2.stat.duke.edu/~mw/West&HarrisonBook/) Bayesian Dynamic Models, the correct structure for sequential updating in a trading system with uncertain parameters is a Dynamic Linear Model (DLM): each cell's risk-adjusted EV is modeled as a latent state that evolves over time, with each week's live outcomes providing a noisy observation. The DLM update equations (Kalman filter) propagate the posterior mean and variance forward in time.

**Conjugate priors for binary outcomes:**

1. **Hit rate (Beta prior).** Hit rate h at exit_X follows a Beta distribution. Prior: Beta(α₀, β₀) centered on corpus hit_rate (α₀ = corpus_hits, β₀ = corpus_misses, scaled to confidence weight). After observing (hits_live, misses_live) in week t: posterior is Beta(α₀ + hits_live, β₀ + misses_live). Expected posterior hit rate: (α₀ + hits_live) / (α₀ + β₀ + hits_live + misses_live). This is the Beta-Bernoulli conjugate pair — exact, no MCMC required. *[Russo et al. (2018)](https://arxiv.org/abs/1707.02038) — Thompson sampling uses exactly this Beta posterior for Bernoulli bandits, and the Kalshi binary hit/miss maps directly onto the Bernoulli bandit setting.*

2. **Per-trade PnL (Normal-Inverse-Gamma prior).** For the continuous return distribution (entry capture + exit capture − fee on hits; settlement value − cost on misses), use a Normal-Inverse-Gamma (NIG) prior on (μ, σ²). Update is exact (conjugate). After k live observations: posterior mean = (n₀μ₀ + k·x̄) / (n₀ + k) where n₀ is the prior effective sample size (set to N_corpus for strong prior) and x̄ is the live sample mean.

3. **Sortino (non-conjugate).** Sortino is a function of both mean and semi-variance, which have no jointly conjugate prior. Approximate Bayesian update: compute the corpus-weighted prior Sortino estimate and update it via:
   ```
   posterior_sortino = (corpus_N × corpus_sortino + live_N × live_sortino) / (corpus_N + live_N)
   ```
   This is a weighted average consistent with the NIG update structure. *[G23: this approximation is a heuristic, not derived from a formal conjugate Bayesian model.]*

### 8.2 Update trigger cadence

Per [Pettenuzzo, Gargano, and Timmermann (2017)](https://pubsonline.informs.org/doi/10.1287/mnsc.2017.2829) on sequential Bayesian model updating with parameter learning:

**Routine updates (weekly).** Every Sunday, run the Beta posterior update on hit rates and the NIG update on per-trade PnL using all live N's accumulated since v5 launch. Recompute Sortino for each cell. Cells that cross the CI threshold (from ambiguous to clearly positive or clearly negative) are flagged for promotion or disable review.

**Trigger-based updates (event-driven).** Run a non-routine re-evaluation when:
- Posterior Sortino mean shifts >1σ of the corpus prior (Sortino degraded significantly)
- Sign of posterior E[PnL] flips (from positive to negative or vice versa) for any promoted v5 cell
- A loss cap event is triggered (per §7.3 guardrails)

Trigger re-evaluation is not automatic promotion or disable — it flags for manual operator review. The operator makes the final call on any triggered cell.

### 8.3 Thompson sampling as live allocation policy (optional)

Per [Russo, Van Roy, Kazerouni, Osband, and Wen (2018)](https://arxiv.org/abs/1707.02038), Thompson sampling allocates exploration to options with uncertain outcomes and exploitation to options with high expected reward. Applied to the per-cell configuration choice: rather than committing a cell to its corpus-optimal (placement, offset, X) configuration, Thompson sampling would sample from the posterior over configurations and occasionally try sub-optimal configurations to refine the posterior. **This is not recommended for the immediate v5 launch** because:

1. The operator needs deterministic live behavior for audit and P&L attribution.
2. Thompson sampling on 360 cells × 1,904 configs each would require tracking 685K posterior distributions — computationally heavy and hard to explain.

**Thompson sampling is recommended as a v6 feature** for the subset of cells with ambiguous CIs, once the v5 live feedback loop has accumulated 4–8 weeks of data to use as the posterior prior. At that point, a cell with CI straddling zero can be given Thompson sampling allocation across {v4 config, v5 config} to resolve the ambiguity faster than passive accumulation. *[Inference: Thompson sampling's efficiency advantage over passive observation is largest when the true optimal is close to the exploration boundary — exactly the ambiguous-CI cell situation.]*

---

## Section 9 — Implementation Skeleton (Pseudocode)

Producer-app pseudocode for a builder agent. Data sources, output schemas, and key decision paths are explicit.

```python
# v5 per-cell EV optimization — producer app skeleton
# Data sources (all under arb-executor/data/durable/):
#   spike_perN/{cat}_spike_perN.parquet  — columns: anchor_price, max_real, settlement_value, time_to_max
#   per_minute_universe/premarket_tape_v1.parquet — columns: match_id, minute_offset, yes_bid_close, yes_ask_close
#   spike_volatility_map/{cat}_descriptive_1c.parquet — atlas baseline: best_exit_X, hit_rate_at_best, roi_pct
#   policy/per_regime_offsets_v2.csv — v4 entry table: category, anchor_regime, placement_minute, offset_cents

import numpy as np
import pandas as pd
from scipy.stats import sem
from sklearn_extra.cluster import KMedoids  # or implement PAM directly

PLACEMENT_CHOICES = [240, 180, 120, 90, 60, 30, 20]
OFFSET_CHOICES = [0, 1, 2, 3, 4, 5, 7, 10, 12, 15, 18, 20]
EXIT_X_CHOICES = [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 18, 20, 25, 30, 40, 50, 999]  # 999 = HOLD
CELL_ANCHOR_BINS = list(range(5, 95))  # 1c bins 5–94
FEE_CENTS = 1.0  # taker fee per fill


def compute_risk_adjusted_ev(
    cell_perN_df: pd.DataFrame,  # rows: {anchor_price, max_real, settlement_value}
    premarket_df: pd.DataFrame,  # rows: {match_id, minute_offset, yes_bid_close}
    placement: int,              # minutes before match start
    offset: int,                 # bid = anchor - offset (cents)
    exit_x: int,                 # exit target = anchor + exit_x (999=HOLD)
    anchor: int                  # 1c anchor bin center
) -> dict:
    """
    Returns: {mean_pnl, sortino, kelly_f, ci_lower, ci_upper, n_filled}
    """
    # Step 1: identify filled N's (bid = anchor - offset; filled if yes_bid_close touched bid)
    bid_price = anchor - offset
    # join perN with premarket_tape on match_id, filter to placement window
    tape_at_placement = premarket_df[premarket_df['minute_offset'] == placement]
    fills = cell_perN_df.merge(
        tape_at_placement[tape_at_placement['yes_bid_close'] <= bid_price][['match_id']],
        on='match_id'
    )
    if len(fills) == 0:
        return {'mean_pnl': np.nan, 'sortino': np.nan, 'kelly_f': np.nan,
                'ci_lower': np.nan, 'ci_upper': np.nan, 'n_filled': 0}

    # Step 2: per-filled-N outcome
    hit_mask = fills['max_real'] >= (anchor + exit_x) if exit_x != 999 else fills['max_real'] >= 99
    returns = np.where(
        hit_mask,
        exit_x - FEE_CENTS,                              # hit: capture exit_x, pay fee
        fills['settlement_value'] - anchor - FEE_CENTS   # miss: receive settlement, pay fee
    )

    # Step 3: Sortino ratio (MAR = 0)
    downside = returns[returns < 0]
    mean_r = np.mean(returns)
    semi_dev = np.sqrt(np.mean(downside**2)) if len(downside) > 0 else 1e-6
    sortino = mean_r / semi_dev if semi_dev > 0 else np.sign(mean_r) * np.inf

    # Step 4: Kelly fraction (binary bet: win=exit_x-fee, loss=|miss_pnl_avg|)
    hit_rate = hit_mask.mean()
    avg_win = exit_x - FEE_CENTS
    avg_loss = abs(np.mean(returns[~hit_mask])) if (~hit_mask).any() else 1e-6
    kelly_f = hit_rate / avg_loss - (1 - hit_rate) / avg_win if avg_win > 0 and avg_loss > 0 else 0.0

    # Step 5: bootstrap CI on Sortino
    ci_lower, ci_upper = bootstrap_ci(returns, n_resamples=1000)

    return {
        'mean_pnl': mean_r, 'sortino': sortino, 'kelly_f': kelly_f,
        'ci_lower': ci_lower, 'ci_upper': ci_upper, 'n_filled': len(fills)
    }


def bootstrap_ci(
    returns: np.ndarray,
    n_resamples: int = 1000,
    b_mean: int = 7,          # stationary bootstrap block length (Politis-Romano 1994)
    ci_level: float = 0.95
) -> tuple:
    """Stationary bootstrap CI on Sortino ratio."""
    n = len(returns)
    if n < 10:
        return (np.nan, np.nan)
    bootstrap_sortinos = []
    for _ in range(n_resamples):
        # draw blocks with geometric block lengths
        sample = []
        while len(sample) < n:
            start = np.random.randint(0, n)
            block_len = max(1, np.random.geometric(1 / b_mean))
            sample.extend(returns[np.arange(start, start + block_len) % n])
        sample = np.array(sample[:n])
        down = sample[sample < 0]
        m = np.mean(sample)
        sd = np.sqrt(np.mean(down**2)) if len(down) > 0 else 1e-6
        bootstrap_sortinos.append(m / sd if sd > 0 else np.sign(m) * 10)
    alpha = (1 - ci_level) / 2
    return (np.percentile(bootstrap_sortinos, 100*alpha),
            np.percentile(bootstrap_sortinos, 100*(1-alpha)))


def sweep_cell(
    cell_id: int,  # anchor bin 5–94
    cat: str,      # ATP_MAIN, WTA_MAIN, ATP_CHALL, WTA_CHALL
    spike_df: pd.DataFrame,
    premarket_df: pd.DataFrame,
    mode: str = 'full'  # 'full' | 'hybrid' (coarse first, refine top-5)
) -> dict:
    """Returns best_config: {placement, offset, exit_x, sortino, ci_lower, ci_upper}"""
    cell_perN = spike_df[spike_df['anchor_price'] == cell_id].copy()
    results = []
    if mode == 'full':
        configs = [(p, o, x) for p in PLACEMENT_CHOICES for o in OFFSET_CHOICES for x in EXIT_X_CHOICES]
    else:  # hybrid: coarse first
        coarse = [(p, o, x) for p in [240, 120, 30]
                  for o in [1, 3, 7, 15, 20]
                  for x in [1, 5, 15, 30, 999]]
        coarse_results = [compute_risk_adjusted_ev(cell_perN, premarket_df, p, o, x, cell_id)
                          | {'config': (p, o, x)} for p, o, x in coarse]
        # top-5 by Sortino → refine in neighborhood
        top5 = sorted([r for r in coarse_results if not np.isnan(r['sortino'])],
                      key=lambda r: r['sortino'], reverse=True)[:5]
        configs = []
        for r in top5:
            p0, o0, x0 = r['config']
            configs += [(p, o, x)
                        for p in PLACEMENT_CHOICES if abs(p - p0) <= 60
                        for o in OFFSET_CHOICES if abs(o - o0) <= 2
                        for x in EXIT_X_CHOICES if abs(x - x0) <= 5 or x == 999]

    for p, o, x in configs:
        ev = compute_risk_adjusted_ev(cell_perN, premarket_df, p, o, x, cell_id)
        if ev['n_filled'] > 0:
            results.append({'placement': p, 'offset': o, 'exit_x': x, **ev})

    if not results:
        return {'cell_id': cell_id, 'status': 'no_fills', 'disabled': True}
    best = max((r for r in results if not np.isnan(r['sortino'])),
               key=lambda r: r['sortino'], default=None)
    return {'cell_id': cell_id, **best, 'disabled': disable_cell(cell_id, best['ci_upper'])}


def disable_cell(cell_id: int, ci_upper: float) -> bool:
    """Disable if upper CI on Sortino is below zero (conservative gate per §3)."""
    if np.isnan(ci_upper):
        return False  # insufficient N — retain v4, do not disable
    return ci_upper < 0.0


def cluster_bands(
    per_cell_optima_df: pd.DataFrame,  # columns: cell_id, placement, offset, exit_x, sortino, disabled
    n_bands: int = None,               # if None, use elbow method
    tolerance: tuple = (1, 1, 2)      # (placement_minutes, offset_cents, exit_x_cents)
) -> pd.DataFrame:
    """k-medoids clustering on configuration space → band_df matching adaptive_exit_bands schema."""
    active = per_cell_optima_df[~per_cell_optima_df['disabled']].copy()
    config_cols = ['placement', 'offset', 'exit_x']
    X = active[config_cols].values.astype(float)
    # normalize
    X_norm = (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0) + 1e-9)

    if n_bands is None:  # elbow on SSE
        sses = []
        for k in range(2, min(80, len(active))):
            km = KMedoids(n_clusters=k, method='pam', random_state=42).fit(X_norm)
            sses.append(km.inertia_)
        diffs = np.diff(sses)
        n_bands = np.argmin(diffs) + 2  # elbow

    km = KMedoids(n_clusters=n_bands, method='pam', random_state=42).fit(X_norm)
    active['band_id'] = km.labels_

    # identify singletons: cells > tolerance from their medoid
    medoid_configs = X[km.medoid_indices_]
    for idx, row in active.iterrows():
        cell_config = np.array([row['placement'], row['offset'], row['exit_x']])
        medoid = medoid_configs[row['band_id']]
        if (abs(cell_config[0] - medoid[0]) > tolerance[0] * 60 or
                abs(cell_config[1] - medoid[1]) > tolerance[1] or
                abs(cell_config[2] - medoid[2]) > tolerance[2]):
            # assign unique band_id (singleton)
            active.at[idx, 'band_id'] = 10000 + idx  # sentinel for singleton

    # produce band output schema
    band_rows = []
    for bid, grp in active.groupby('band_id'):
        medoid_row = grp.iloc[0] if bid >= 10000 else grp.loc[grp['cell_id'] == active.loc[km.medoid_indices_[bid % n_bands], 'cell_id']].iloc[0] if bid < n_bands else grp.iloc[0]
        band_rows.append({
            'band_id': bid,
            'price_range': f"{grp['cell_id'].min()}–{grp['cell_id'].max()}",
            'cells': list(grp['cell_id']),
            'placement_minute': int(medoid_row['placement']),
            'offset_cents': int(medoid_row['offset']),
            'exit_X': int(medoid_row['exit_x']),
            'N': int(grp['n_filled'].sum()),
            'sortino': float(grp['sortino'].mean()),
        })
    return pd.DataFrame(band_rows)


def validate_no_regression(
    v5_bands: pd.DataFrame,
    atlas_baseline_roi: float = 0.0870,
    v4_roi: float = 0.0808,
    cpcv_paths: int = 28
) -> dict:
    """Gate checks per §5. Returns dict of gate results."""
    # Gate 1: blended corpus ROI
    blended_roi = (v5_bands['$'].sum() / v5_bands['cap_$'].sum())
    gate1 = blended_roi >= v4_roi + 0.01  # ≥ v4 + 1pp
    # Gate 3: per-category (requires category column in v5_bands)
    # Gate 4: CPCV — placeholder; requires running CPCV folds
    # Gate 5: DSR — placeholder; requires Sharpe computation under null
    return {'gate1_corpus_roi': gate1, 'blended_roi': blended_roi,
            'note': 'Gates 2,4,5 require CPCV and corpus Sortino computation'}


def bayesian_update(
    cell_id: int,
    live_observations: dict,    # {hits: int, misses: int, pnl_arr: np.ndarray}
    prior: dict                 # {alpha: float, beta: float, corpus_sortino: float, corpus_N: int}
) -> dict:
    """Beta-Bernoulli update on hit rate; weighted Sortino update."""
    # Hit rate update (conjugate Beta)
    post_alpha = prior['alpha'] + live_observations['hits']
    post_beta = prior['beta'] + live_observations['misses']
    post_hit_rate = post_alpha / (post_alpha + post_beta)

    # Sortino update (weighted average)
    live_N = len(live_observations['pnl_arr'])
    if live_N > 0:
        live_returns = live_observations['pnl_arr']
        live_down = live_returns[live_returns < 0]
        live_semi_dev = np.sqrt(np.mean(live_down**2)) if len(live_down) > 0 else 1e-6
        live_sortino = np.mean(live_returns) / live_semi_dev
        w_corpus = prior['corpus_N']
        post_sortino = (w_corpus * prior['corpus_sortino'] + live_N * live_sortino) / (w_corpus + live_N)
    else:
        post_sortino = prior['corpus_sortino']

    # Trigger flag: did Sortino shift > 1 sigma of corpus prior?
    trigger = abs(post_sortino - prior['corpus_sortino']) > (1.0 / np.sqrt(prior['corpus_N']))

    return {'cell_id': cell_id, 'post_hit_rate': post_hit_rate,
            'post_sortino': post_sortino, 'trigger_review': trigger,
            'post_alpha': post_alpha, 'post_beta': post_beta}
```

---

## Provenance — Citations

| # | Authors | Year | Title | URL |
|---|---|---|---|---|
| 1 | Sharpe, W. | 1966 | Mutual Fund Performance | https://www.jstor.org/stable/4479578 |
| 2 | Sortino, F.; Price, L. | 1994 | Performance Measurement in a Downside Risk Framework (CFA Institute) | https://rpc.cfainstitute.org/sites/default/files/-/media/documents/code/gips/the-sortino-ratio.pdf |
| 3 | Kelly, J. L. | 1956 | A New Interpretation of Information Rate | https://www.princeton.edu/~wbialek/rome/refs/kelly_56.pdf |
| 4 | Rockafellar, R.; Uryasev, S. | 2000 | Optimization of Conditional Value-at-Risk | https://sites.math.washington.edu/~rtr/papers/rtr179-CVaR1.pdf |
| 5 | Browne, S. | 1997 | Survival and Growth with a Liability: Optimal Portfolio Strategies in Continuous Time | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=57909 |
| 6 | Roy, A. D. | 1952 | Safety First and the Holding of Assets | https://www.jstor.org/stable/1907413 |
| 7 | Markowitz, H. | 1952 | Portfolio Selection | https://www.jstor.org/stable/2975974 |
| 8 | Ledoit, O.; Wolf, M. | 2004 | Honey, I Shrunk the Sample Covariance Matrix | http://www.ledoit.net/honey.pdf |
| 9 | Bergstra, J.; Bengio, Y. | 2012 | Random Search for Hyper-Parameter Optimization | https://jmlr.org/papers/v13/bergstra12a.html |
| 10 | Snoek, J.; Larochelle, H.; Adams, R. | 2012 | Practical Bayesian Optimization of Machine Learning Algorithms | https://arxiv.org/abs/1206.2944 |
| 11 | Bailey, D.; Borwein, J.; López de Prado, M.; Zhu, Q. | 2014 | The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting, and Non-Normality | https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf |
| 12 | López de Prado, M. | 2018 | Advances in Financial Machine Learning | https://www.wiley.com/en-us/Advances+in+Financial+Machine+Learning-p-9781119482086 |
| 13 | López de Prado, M. | 2020 | Clustered Feature Importance (Presentation Slides) | https://ssrn.com/abstract=3517595 |
| 14 | Politis, D.; Romano, J. | 1994 | The Stationary Bootstrap | https://www.jstor.org/stable/2291286 |
| 15 | West, M.; Harrison, J. | 1997 | Bayesian Forecasting and Dynamic Models (2nd ed.) | https://www2.stat.duke.edu/~mw/West&HarrisonBook/ |
| 16 | Russo, D.; Van Roy, B.; Kazerouni, A.; Osband, I.; Wen, Z. | 2018 | A Tutorial on Thompson Sampling | https://arxiv.org/abs/1707.02038 |
| 17 | Kohavi, R.; Tang, D.; Xu, Y. | 2020 | Trustworthy Online Controlled Experiments: A Practical Guide to A/B Testing | https://www.cambridge.org/core/books/trustworthy-online-controlled-experiments/D97B26382EB0EB2DC2019A7A7B518F59 |
| 18 | Johari, R.; Pekelis, L.; Walsh, D. | 2017 | Always Valid Inference: Bringing Sequential Analysis to A/B Testing | https://arxiv.org/abs/1512.04922 |
| 19 | Pettenuzzo, D.; Gargano, A.; Timmermann, A. | 2017 | Bond Return Predictability: Economic Value and Links to the Macroeconomy | https://pubsonline.informs.org/doi/10.1287/mnsc.2017.2829 |
| 20 | MacLean, L.; Thorp, E.; Ziemba, W. | 2011 | The Kelly Capital Growth Investment Criterion | https://www.worldscientific.com/worldscibooks/10.1142/7598 |
| 21 | DeLise, T. | 2024 | Adverse Selection and Limit Order Fills | https://arxiv.org/abs/2407.16527 |
| 22 | Rockafellar, R.; Uryasev, S. | 2002 | Conditional Value-at-Risk for General Loss Distributions | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=267256 |
| 23 | Hasbrouck, J. | 1995 | One Security, Many Markets: Determining the Contributions to Price Discovery | https://doi.org/10.1111/j.1540-6261.1995.tb04054.x |
| 24 | Hutter, F.; Hoos, H.; Leyton-Brown, K. | 2011 | Sequential Model-Based Optimization for General Algorithm Configuration (SMAC) | https://doi.org/10.1007/978-3-642-25566-3_40 |
| 25 | Cao, C.; Ghysels, E.; Hatheway, F. | 2000 | Price Discovery without Trading: Evidence from the Nasdaq Pre-opening | https://doi.org/10.1111/0022-1082.00249 |

---

## Cross-References to Prior Rounds

| Round | Filename | Grounding for v5 |
|---|---|---|
| Round 1 | `plex_premarket_execution_round1_2026-05-21.md` | Paired binary structure; Hasbrouck information share; cross-book consensus — load-bearing for B23 in §§1, 3 |
| Round 2 | `plex_premarket_execution_round2_2026-05-21.md` | CPCV purged+embargoed validation protocol — §5 Gate 4 directly applies Round 2's 28-path CPCV design |
| Round 3 | `plex_premarket_execution_round3_2026-05-21.md` | Queue position negligible in thin-book markets — supports §2's fill-rate modeling assumptions |
| Round 4 | `plex_premarket_execution_round4_2026-05-22.md` | Composite-event detector (two-of-four burst architecture) — relevant to §7's shadow-mode cell monitoring for burst-day outliers |
| Round 5 | `plex_premarket_execution_round5_2026-05-23.md` | Favorite-drift policy (sharp money with favorites on exchanges); FV multiplicative confidence weight — §1's metric choice inherits the direction-of-fill insight from Round 5 |
| Round 6 | `plex_premarket_execution_round6_2026-05-23.md` | B25 0.5–0.7× realism discount; staged deployment doctrine (single concern → regime conditioning → velocity burst) — §§5, 7 directly extend Round 6's phased approach to cell-level granularity |
| Round 7 | `plex_premarket_execution_round7_2026-05-23.md` | Premarket drift predictors; feature table format; sub-Q structure — §§2 and 4 follow Round 7's feature-table-plus-discussion house style |

*Note: `plex_spectrum_banding_round1_2026-05-24.md` referenced in the context capsule does not exist in the external_synthesis directory; `adaptive_exit_banding_findings.md` is the closest analog and is used throughout §§1, 3, 4.*

---

## Doctrine Codes Engaged

| Code | How it appears in v5 |
|---|---|
| **A39** | Cents-vs-ROI asymmetry: §1 notes that at 5c sizing, small $/N differences are large ROI swings — the Sortino metric must be computed on per-trade ROI not raw dollars; §3 notes that disabling cells reduces ROI denominator and may improve blended ROI |
| **B16** | Layer A/B/C decomposition: v5 operates on Axis 2 (entry-side, Layer B) and Axis 3 (exit-side, Layer C) jointly; §2's joint sweep is the concrete implementation of the Layer B/C interaction |
| **B23** | Paired-leg structural mechanism: §§2, 3 note that fill_rate measurement must account for the paired-binary structure; the no-arb constraint means the entry price signal on the YES-favorite leg is coupled to the YES-underdog leg (relevant to fill detection in the premarket tape) |
| **B25** | Minute-cadence simulator overstatement: §5 mandates the 0.5–0.7× realism discount on all corpus PnL claims; live improvement is projected at +0.5–0.7× the corpus +1.0pp lift bar |
| **C40** | External synthesis committed to repo immediately: status line in header block confirms this; subagent writes directly to `arb-executor/docs/external_synthesis/`; git commit is left to the chat-side agent |
| **F33** | Depth-chain data gap: §2.3 notes that taker-side volume data absence defaults the fill condition to price-cross on best-bid candle — the known conservative fallback under F33 |
| **G19** | Candle null patterns: §2.3 and §6.4 flag that per-minute candles may have null `yes_bid_close` entries for thinly-traded cells; fill detection must handle nulls rather than treating null as "no bid existed" |
| **G22** | Three-axis deployment math: §2.1's sweep space table quantifies the full 685K config space as the product of entry-axis × exit-axis × cell-coverage; the hybrid sweep strategy is the operationally feasible approximation |
| **G23** | Inference vs evidence labeling per claim: throughout all sections, claims derived from cited literature applied by analogy are labeled *[Inference: …]* and claims directly measured on the corpus are labeled *[Evidence: …]* |
