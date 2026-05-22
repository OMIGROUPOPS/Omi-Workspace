# Plex Premarket Execution Synthesis — Round 2: Feature Importance, Model Class Shortlist, Train/Val/Test Split Design

**Source:** Plex (Perplexity) literature synthesis
**Date:** 2026-05-21
**Prompt context:** Round 2 was asked to synthesize literature on three sub-questions bearing on the predictive model layer for premarket maker-bid placement: (1) which features in the per-minute state vector (own-leg BBO, partner-leg observables, behavioral depth proxies, FV anchor signals, distortion features, regime labels, time-to-match-start) are most likely predictive of fill probability and post-fill forward return, based on related microstructure and sports-betting literature; (2) a model class shortlist covering gradient-boosted trees, logistic regression, HMM, reinforcement learning, and several additional candidates (two-stage models, Bayesian hierarchical, isotonic calibration, imitation learning), with comparative strengths and weaknesses in this specific setting; and (3) train/validate/test split design that respects both time-ordering and paired-event leakage (the two legs of the same event share event_ticker and represent correlated observations).
**Status:** External synthesis — for integration by chat-side Opus into the U4 Phase 3 build and bid-laying policy spec. Per LESSONS C40, external synthesis is committed to repo immediately, not held in chat-side context only.

---

## 1. Feature Importance: Fill Probability and Post-Fill Forward Return Predictors

### 1a. Order-book imbalance as the canonical fill-probability and short-horizon-return predictor

The core empirical regularity in microstructure literature is that top-of-book order-book imbalance (OBI) — the ratio of bid queue size to total bid+ask queue size at the best price — is among the strongest short-horizon predictors of both fill probability for resting maker orders and the direction of the next price move.

Cont, Kukanov, and Stoikov (2014, "The Price Impact of Order Book Events," *Journal of Financial Econometrics*, arXiv:1011.6402, https://arxiv.org/abs/1011.6402) establish the foundational empirical result: OBI measured at top-of-book is a statistically significant and economically meaningful predictor of the direction and magnitude of the next mid-price change at horizons from 1 to 10 ticks. Their price impact decomposition shows that aggressive orders (market buys against the ask) carry more price impact per share when OBI is already imbalanced toward the ask (ask queue thin, bid queue thick), confirming that OBI encodes information about which side is under pressure.

In the operator's per_minute_features.parquet, the most direct OBI proxies are:
- `bid_consumption_velocity` and `ask_consumption_velocity`: inferred from trade tape, these capture the rate at which the bid vs. ask side is being hit — a high `ask_consumption_velocity` relative to `bid_consumption_velocity` indicates aggressive buying (takers crossing ask), which will compress the ask toward the resting maker bid.
- `price_levels_consumed_in_minute`: a proxy for how many price levels of depth were consumed by takers in the minute — a high value indicates a wide sweep, thin book, or both.
- `trade_clustering_in_minute` (std of inter-trade gap times): high clustering (low std of inter-trade gaps = trades arriving in bursts) is consistent with informed order flow arriving in a concentrated period.

For a resting maker bid at the best bid price, **fill probability is directly related to ask-side consumption velocity**: maker bids fill when takers cross the spread from the ask side. Therefore `ask_consumption_velocity` is the closest empirical predictor of fill timing, and `bid_consumption_velocity` is the closest proxy for adverse-selection risk (high bid_consumption_velocity = someone is aggressively hitting the bid below yours, which means the book is being swept toward lower prices).

**Partner-leg OBI.** By analogy (inferential bridge — no direct paper studies this for binary pairs), the partner leg's `partner_taker_flow_in_minute` and `partner_volume_in_minute` encode information about correlated order flow. If the partner leg is seeing elevated taker flow on the sell side (someone hitting bids), the no-arb sum constraint implies that the own leg should also be depressing — an adverse signal for a resting bid on the own leg.

Lucchese, Pakkanen, and Veraart (2023, "The Short-Term Predictability of Returns in Order Book Markets: A Deep Learning Perspective," arXiv:2211.13777, https://arxiv.org/abs/2211.13777) find in a large-scale analysis that top-of-book volume representation (the bid/ask queue sizes at the top 5-10 levels) carries most of the predictable signal in high-frequency returns — deep-book features contribute marginally over top-of-book. This is directly relevant given F33 (depth-chain gap): the operator has top-of-book only (BBO), and this literature confirms that top-of-book carries the bulk of the signal. The finding holds across equities and is likely directionally correct for Kalshi, though the extremely thin book (10-50 ct typical BBO size) means that OBI signals will be noisier and more episodic than in equity markets.

### 1b. Cross-venue consensus delta as a convergence-direction signal

The `fv_delta = kalshi_fill_price − consensus_fv` variable is the most structurally novel feature in the operator's dataset — no prior academic work studies a Kalshi-vs-Pinnacle+EU-books consensus gap at minute resolution.

The closest literature is cross-venue price discovery research. Hasbrouck (1995, "One Security, Many Markets," *Journal of Finance*) shows that in multi-venue equity markets, the best predictor of short-horizon price direction in any one venue is the deviation of that venue's price from the efficient price estimated from all venues jointly. By direct analogy: `fv_delta` = Kalshi's deviation from the (Pinnacle-anchored) efficient price estimate. When `fv_delta` < 0 (DISCOUNT: Kalshi price below consensus FV), the expected convergence direction is upward, making a maker bid attractive. When `fv_delta` > 0 (PREMIUM: Kalshi price above consensus FV), the expected convergence direction is downward, making a maker bid unattractive regardless of the atlas cell edge (the atlas anchors on historical T-20m taker prices, and if those prices were already above consensus FV, the atlas edge may be partly a measurement artifact of a period where Kalshi was systematically expensive).

**Confidence interval note (A21).** The `fv_delta` convergence-direction signal's strength depends on: (a) how frequently Kalshi converges to consensus before match start (empirically unknow from external literature; must be measured from per_minute_features.parquet); (b) the precision of the `consensus_fv` estimate (30-46 books with liquidity-weighted aggregation; precision varies by event popularity and coverage rate). Neither CI can be stated from external literature — they are corpus-specific.

**Literature analogy: ETF-NAV basis.** ETF-NAV basis studies (Petajisto 2017, "Inefficiencies in the Pricing of Exchange-Traded Funds," *Financial Analysts Journal*) consistently find that ETF price deviations from NAV are mean-reverting and exploitable by market participants with authorized participant (AP) access. The Kalshi-consensus gap is analogous but with a higher friction coefficient: Kalshi is not arbitrageable by a pure AP mechanism (there is no physical delivery mechanism), so convergence depends entirely on informed trading pressure from participants who simultaneously monitor Kalshi and external books. This means the convergence speed will be slower and more variable than ETF-NAV convergence, and the optimal bid placement will need to account for the probability that the gap does not fully close before match start.

### 1c. Paired-leg distortion features as microstructure-stress signals

`paired_arb_gap_maker = 1.00 − paired_yes_bid_sum` and `paired_mid_sum` deviation from $1 are direct descendants of the paired-asset arbitrage literature. Their interpretive value:

- Large positive `paired_arb_gap_maker` (e.g., 0.10): both legs' bids are far from $1 combined — the market is pricing the two legs as if their probabilities don't sum to 1 at the bid level. This indicates either (a) the book is in formation phase with sparse liquidity, (b) both sides are being held off-market pending information, or (c) there is a structural imbalance in which one leg has been aggressively sold and the other hasn't adjusted.
- `paired_mid_sum` significantly below $1: both mid-prices are depressed (low activity, early formation).
- `paired_arb_gap_taker = paired_yes_ask_sum − 1.00` negative: the two asks sum to less than $1 — a taker could simultaneously buy both YES contracts for less than $1 and guarantee a profit. This is a true taker arbitrage signal and, when negative, indicates an anomaly in the book that sophisticated takers will exploit instantly in liquid markets; in Kalshi tennis, it may persist briefly due to low monitoring intensity.

The relevance for fill probability: when `paired_arb_gap_maker` is large, a maker bid on either leg at the current BBO is likely to fill because takers have an incentive to hit one side to resolve the distortion. When the gap is near zero, the book is nearly coherent and maker fills depend primarily on directional order flow. This makes `paired_arb_gap_maker` a fill-probability amplifier — high gap = elevated fill probability — but it also signals a thinner, more stressed book where adverse-selection risk is higher (inference by analogy to thin-book dynamics in illiquid equity pairs).

**Inference vs. evidence note.** No academic paper directly studies `paired_arb_gap_maker` as a feature in a prediction model for Kalshi-like markets. This is inferential from (a) Rana et al. (2026) ParlayMarket joint-leg coherence analysis, (b) put-call parity arbitrage mechanics, (c) Groeger (2016) prediction market LOB imbalance results. The corpus analysis on per_minute_features.parquet is the primary source of evidence for this feature's predictive power.

### 1d. Time-to-match-start as a non-stationarity axis

The strong non-stationarity of market microstructure across time-to-event-start is well-documented. For prediction markets, Pennock et al. (2001, "Modelling Information Incorporation in Markets, with Application to Detecting and Explaining Events," arXiv:1301.0594, https://arxiv.org/abs/1301.0594) show that prediction market prices incorporate information at different rates depending on the event horizon — closer to the event, information from multiple sources converges faster, and the market is more efficient. This means features like OBI, fv_delta, and trade_clustering_in_minute have different predictive relationships with fill probability and forward return depending on `time_to_match_start_min`.

The practical implication: models trained on pooled premarket data (all minutes from T-120m to T-0) may suffer from non-stationarity-induced heteroscedasticity. The E12 premarket phase regime labels (formation / premarket stable / in_match / settlement_zone) partially address this by encoding the phase, but within each phase, `time_to_match_start_min` is a continuous non-stationarity axis that should be either: (a) included as a feature explicitly, (b) used to stratify training, or (c) modeled through a regime-switching component. This is the theoretical motivation for the HMM model class discussed in Section 2c below.

### 1e. Feature priority summary (with CI caveat)

| Feature group | Relevance to fill probability | Relevance to post-fill forward return | Evidence quality |
|---|---|---|---|
| `ask_consumption_velocity` (own) | High: direct predictor of taker aggression on ask | Moderate: high taker buy pressure → price rises after fill | Inferential from Cont-Kukanov-Stoikov 2014 + Groeger 2016 |
| `bid_consumption_velocity` (own) | Moderate: high = adverse signal (sellers hitting bid) | Negative: filled when price is falling | Same |
| `partner_taker_flow_in_minute` | Moderate: correlated via no-arb sum | Negative: correlated leg flow adverse | Inference from Rana et al. 2026 + put-call parity |
| `paired_arb_gap_maker` | Elevated fill probability when large | Mixed: large gap may mean stressed book | Inferential |
| `fv_delta` (own leg) | Low direct effect on fill | High: DISCOUNT → convergence upward | Hasbrouck 1995 analogy; corpus-dependent CI |
| `partner fv_delta` | Moderate: partner PREMIUM → partner price may fall, own rises | Similar | Same |
| `price_levels_consumed_in_minute` | High: thin book → fast fill when taker sweeps | Mixed | Inferential from LOB literature |
| `trade_clustering_in_minute` | Moderate: burst flow → fill likely | Negative: burst = informed arrival | Inferred from VPIN literature |
| `time_to_match_start_min` | Interaction: changes meaning of all other features | High: regime marker | E12 premarket phase structure |
| `open_interest` / `oi_delta` | Low-moderate: broader interest proxy | Low | F33 depth gap constraint |
| `regime_classification` label | High: encodes phase non-stationarity | High: feature meaning shifts by regime | E12 direct |

*CIs on feature importances:* All importances above are inferential from adjacent literature; no direct empirical study of per_minute_features.parquet feature importance has been conducted. In-corpus permutation importance and SHAP analysis on a held-out test set are the correct empirical source (A21 CI discipline applies — these should be reported with bootstrap confidence intervals on the importance scores).

---

## 2. Model Class Shortlist

### 2a. Gradient-boosted trees (GBT) per-cell

**Strengths.** GBT (XGBoost, LightGBM, CatBoost) handles non-linear feature interactions without explicit engineering, provides interpretable feature importance via SHAP values, and is robust to outliers and monotone transformations of features. López de Prado (2018, *Advances in Financial Machine Learning*, Wiley, Chapter 8) recommends GBT as the dominant model class for financial ML applications, citing its robustness to the mixed feature types and heteroscedastic residuals typical of financial data.

**Weaknesses in this setting.**
1. Per-cell training: with ~90 cells per category and ~16/day for ATP_MAIN, each cell has on the order of 200-600 premarket minutes per cell in a 10-month corpus. This is marginal for GBT — feature importance and split decisions become noisy at N < 500 (A21 anti-small-N). The risk is that GBT finds cell-specific overfits that do not generalize: the operator's note that "per-cell argmax fits do not generalize forward at any tested smoothness penalty" is consistent with this concern.
2. No native temporal structure: GBT treats rows as IID unless features encode sequential dependencies. Without explicit lag features or temporal aggregations, GBT misses within-event premarket dynamics.
3. Per-cell calibration: GBT probability outputs are not natively calibrated; isotonic regression or Platt scaling post-hoc is required for well-calibrated fill-probability estimates (B15 unit-of-decision per-minute requires probability, not just rank ordering).

**Recommendation from literature.** For fill-probability prediction specifically, a well-regularized GBT (moderate max_depth, low learning rate, early stopping on validation log-loss) trained on pooled data across cells — with cell identity as a categorical feature — is more data-efficient than per-cell models and reduces overfitting. This is consistent with the Bayesian hierarchical framing in Section 2e below (partial pooling).

### 2b. Logistic regression per-cell

**Strengths.** Linear in features (with pre-specified interactions/polynomials), naturally calibrated probabilities under logistic likelihood, interpretable coefficients. In microstructure applications, Cartea, Jaimungal, and Penalva (2015) use logistic regression for fill-probability modeling in algorithmic execution contexts, finding it competitive with more complex models when feature engineering is sound.

**Weaknesses.** Linear boundary cannot capture the interaction between `fv_delta` × `paired_arb_gap_maker` × `time_to_match_start_min` that is likely present in the data. Per-cell sample size concern is the same as for GBT. Feature scaling and multicollinearity (own BBO + partner BBO are correlated via no-arb sum) require preprocessing discipline.

**When to prefer.** Logistic regression is a strong baseline for fill-probability modeling when feature engineering is carefully done and the goal is a well-calibrated, interpretable model. It is better suited for the `fv_delta`-driven convergence signal than for the `paired_arb_gap_maker` × `ask_consumption_velocity` interaction, which is non-linear.

### 2c. Hidden Markov Model over premarket-phase × distortion regime

**Strengths.** The HMM explicitly models regime transitions (formation → stable → pregame) as a latent state, with emission distributions for observable features that vary by regime. This directly addresses the time-to-match-start non-stationarity documented in Section 1d. Zabaljauregui and Campi (2020, "Optimal market making under partial information with general intensities," arXiv:1902.01157, https://arxiv.org/abs/1902.01157) study a market-maker with a hidden Markov chain governing order flow regimes and derive optimal quotes as functions of the posterior belief over regime states. Their result: incorporating hidden regime information substantially improves expected PnL relative to models that don't account for regime.

**Weaknesses.** HMM state-space design is non-trivial: how many states, which features are in the emission distribution, what transition structure? With three operator-defined phases (E12), a 3-state HMM is the natural starting point, but the observation granularity (per-minute) means transition dynamics are estimated from limited phase-change events in the corpus. The HMM is also not natively discriminative — it models P(features | state), not P(state, outcome | features), requiring additional integration for the fill-probability and forward-return prediction objectives.

**Recommended use.** HMM is best used as a feature-generation step (estimate the posterior probability of being in each phase, P(phase | feature_history_t), and use these posterior probabilities as additional features in a GBT or logistic model) rather than as the end-to-end prediction model. This is consistent with B14/G17 premarket vs. in-match decomposition — the HMM provides a soft phase label that the downstream model can use.

### 2d. Reinforcement learning policy over per-moment state

**Strengths.** RL end-to-end optimizes the placement decision (bid level, duration, cancellation trigger) as a policy over the per-moment state, capturing the sequential nature of premarket execution that cross-sectional models miss. Zhao and Linetsky (2021) use RL for adverse-selection-aware market-making and demonstrate substantially better risk-adjusted PnL than static rule-based approaches. In the sports-betting context, Terawong and Cliff (2024, "XGBoost Learning of Dynamic Wager Placement for In-Play Betting on an Agent-Based Model of a Sports Betting Exchange," arXiv:2401.06086, https://arxiv.org/abs/2401.06086) use XGBoost-learned decision trees in an RL-like setting for in-play betting and find positive outcomes.

**Weaknesses in this specific setting.**
1. Reward design is the primary risk. The success criterion — fill-at-X within window followed by exit at atlas-cell hindsight-optimal target — is a composite, multi-step reward. RL agents are notoriously sensitive to reward shaping; a poorly designed reward will produce policies that maximize the reward function but not the true economic objective.
2. Data volume: the 10-month corpus gives approximately 9.33M per_minute_features rows but only ~16/day premarket events per ATP_MAIN category. RL requires many policy rollouts to converge; the corpus is too small for off-policy RL without extensive augmentation or simulation.
3. The atlas's hindsight-optimal trace is a supervised signal, not an interactive environment. Using the corpus as an RL environment requires offline RL methods (batch RL), which are technically demanding and prone to distribution shift.

**Recommended framing.** RL is a long-run research direction, not a near-term implementation for the U4 Phase 3 build. The near-term pragmatic path is two-stage supervised learning (Section 2e) with RL as a Phase 4 candidate.

### 2e. Additional candidates worth raising

**Two-stage model (fill model + post-fill return model).** The composite prediction target — fill probability × post-fill forward bounce × exit probability at atlas target — is better decomposed into two calibrated models than trained as a single joint model. Stage 1: P(fill within window | state, bid level). Stage 2: E(forward bounce | fill, state). The bid-laying policy selects bid levels by maximizing Stage1 × Stage2 subject to a price concession constraint. This decomposition is standard in optimal execution literature (Cartea, Jaimungal, Penalva 2015, Chapter 7) and avoids the reward-design problem of joint models. It also enables separate calibration and separate monitoring of each stage.

**Bayesian hierarchical model with cell-level priors.** The 90-cell structure across four categories (360 cells total) with highly heterogeneous N's is exactly the setting where Bayesian hierarchical (partial-pooling) models outperform both per-cell models (overfit, small N) and fully-pooled models (underfit, ignores cell heterogeneity). The hierarchical prior over cell-level coefficients shrinks estimates toward the population mean in proportion to each cell's sample uncertainty. Gelman, Carlin, Stern, et al. (*Bayesian Data Analysis*, 3rd ed.) establish that partial pooling dominates both extremes in the bias-variance tradeoff for hierarchical data structures. The operator's note that per-cell argmax does not generalize is direct evidence that full pooling across cells is needed; hierarchical models provide the principled framework.

**Isotonic regression post-hoc calibration.** GBT probability outputs are systematically uncalibrated (overconfident). Platt scaling (logistic regression on the score) or isotonic regression (monotone non-parametric) applied as a post-processing step is standard practice. Niculescu-Mizil and Caruana (2005, "Predicting Good Probabilities With Supervised Learning," *ICML*) establish that GBT requires calibration while SVMs and random forests require it less. Well-calibrated fill-probability estimates are essential for the bid-improvement threshold decision in Round 3 (B15 unit-of-decision per-minute).

**Imitation learning from atlas hindsight-optimal trace.** The atlas's hindsight-optimal exit-or-hold rules constitute a labeled policy over (cell, state) → outcome. Imitation learning (behavioral cloning or DAgger) treats this trace as an expert demonstration and trains a policy to mimic it. The risk: hindsight optimality is not a feasible policy (it requires knowing the future), so the imitated policy will overfit to ex-post labeling artifacts. This is structurally the same problem as the per-cell argmax overfitting the operator observed. Use only if the atlas's hindsight labels are confirmed to generalize in walk-forward evaluation.

### 2f. Model class comparison table

| Model class | Handles non-linearity | Models temporal structure | Calibrated P(fill) | Small-N robust | Per-cell or pooled | Recommended use |
|---|---|---|---|---|---|---|
| GBT (pooled, cell as feature) | Yes | Via features | After calibration | Moderate | Pooled | Primary baseline for fill model |
| Logistic regression (pooled) | Partial (requires engineering) | Via features | Native | High | Pooled | Strong interpretable baseline |
| HMM (regime detection) | N/A | Yes, latent states | Via posterior | Moderate | Shared across cells | Feature generation (phase posterior) |
| RL (offline/batch) | Yes | Yes, sequential | Via reward | Low | Pooled | Long-run research direction |
| Two-stage supervised | Both stages handle | Via features | Yes, per stage | Moderate | Pooled stages | Near-term recommended architecture |
| Bayesian hierarchical | Partial (linear hierarchy) | Via features | Yes | High | Partial pooling | Near-term recommended for fill model |
| Isotonic calibration | N/A (post-hoc) | N/A | Yes, by construction | N/A | Post any model | Required post-processing |

---

## 3. Train/Validate/Test Split Design

### 3a. The dual leakage problem: time-ordering + paired-leg contamination

Two distinct forms of data leakage threaten ML models on per_minute_features.parquet:

**Type 1: Look-ahead leakage.** Forward-looking labels (`max_yes_bid_forward_{5,15,30,60}min`, `bounce_*`) are computed from future prices. A row at minute T uses prices from minutes T+5, T+15, T+30, T+60. If T+30 falls in a training row and T is in the test row, the training observation contains information from the test period. In a standard chronological cutoff split, this occurs near the cutoff boundary. With a T+60 label, the last 60 minutes of training data before the cutoff are contaminated.

**Type 2: Paired-leg contamination.** The two legs of the same match (player1-YES and player2-YES) are separate rows in the parquet but share `event_ticker`. Their features are partially correlated (through the no-arb sum constraint and the shared information environment). If leg-A is in training and leg-B is in test, the model may learn leg-A's features that implicitly encode leg-B's outcomes — a subtle leakage that standard chronological splits do not prevent. López de Prado (2018, *AFML*, Chapter 7) identifies this pattern explicitly as "label contamination" in multi-row labeling structures.

### 3b. Naive chronological cutoff — risks and mitigations

A naive 7-month train / 1.5-month val / 1.5-month test split (approximate proportions for the 10-month corpus 2025-06-18 → 2026-05-01) provides clean temporal ordering but does not address:

1. **Cross-cutoff paired-leg leakage:** if a match at the train-val boundary has leg-A's early premarket minutes in training and leg-B's later premarket minutes in validation (or the reverse), both types of contamination occur simultaneously. For a 60-minute premarket window, any match whose premarket window spans the cutoff date contributes contaminated rows on both sides.

2. **Label-horizon contamination at boundary:** with forward labels up to T+60min (or T-to-match-start, which could be hours), rows in the last hours/day of training contain labels derived from the validation period.

**Mitigations.** The López de Prado purged + embargoed cross-validation framework (Wikipedia, "Purged cross-validation," https://en.wikipedia.org/wiki/Purged_cross-validation) addresses both: **Purging** removes from training any row whose label formation period overlaps the test/validation period — for a T+60 label, purge the last 60 minutes of training data before the cutoff. **Embargo** adds a buffer after each test fold to prevent leakage from market-reaction lag or auto-correlated features — for Kalshi tennis with 1-hour premarket windows, an embargo of 120 minutes (one full premarket window) after each validation cutoff prevents residual contamination.

For paired-leg leakage specifically: purge at the `event_ticker` level — if any row from event E is in the test set, all rows from event E are excluded from training (both legs, all premarket minutes). This is a stronger purge than standard time-based purging but is the correct unit of contamination for the paired structure (B23 bilateral mechanism).

### 3c. Event-block chronological split — the preferred approach

The preferred architecture for this dataset is:

1. **Group by `event_ticker`** (each match is an event block).
2. **Sort events chronologically** by match start time.
3. **Split at event boundaries**, not row boundaries:
   - Training: all events with match_start before cutoff T1
   - Validation: all events with match_start between T1 and T2
   - Test: all events with match_start after T2
4. **Apply forward-label purge at T1 and T2**: any training event whose latest forward-label timestamp extends into the validation period is excluded from training entirely. For a 60-min label horizon, this means events within 60min before T1 are excluded from training.
5. **Embargo**: events whose first observation is within 120min after T1 (or T2) are excluded from validation (or test) to prevent autocorrelated-feature leakage.

This design eliminates both Type 1 and Type 2 leakage. The cost: the purge and embargo reduce effective training data by approximately one premarket window (~120min of events) at each boundary. For the 10-month corpus with ~16 ATP_MAIN events/day, this is approximately 32-48 events lost to boundary purging, a small fraction of the total.

**Per-category vs. global split.** The four tour categories (ATP_MAIN, WTA_MAIN, ATP_CHALL, WTA_CHALL) have different N's/day (16.4 / 14.9 / 48.9 / 11.1), different market microstructure characteristics, and different cell count compositions. A global split (all categories share the same temporal cutoffs) is simpler and allows cross-category feature sharing in pooled models. A per-category split allows the model to optimize for each category's distinct dynamics but loses cross-category signal. The recommendation from the hierarchical model literature (Gelman et al.): use a global split with category as a feature / hierarchical grouping variable, so the model can learn shared and category-specific patterns simultaneously.

### 3d. Walk-forward / expanding-window evaluation

For assessing generalization over the 10-month corpus with non-stationary microstructure (Kalshi rule changes, seasonal tennis schedule, market maturation), a walk-forward design is more informative than a single train/val/test split. The design:

- **Expanding window**: training period grows from a minimum window (e.g., 3 months) to cover the full corpus up to each test window start.
- **Fixed test window**: each fold tests on a fixed 4-6 week forward window.
- **Purge and embargo** at each fold boundary as above.

López de Prado (2018, AFML) argues that walk-forward evaluation over multiple folds produces a distribution of out-of-sample performance estimates, reducing the risk that the observed OOS performance is specific to a particular regime or dataset realization. This is especially important given the operator's observation that per-cell argmax does not generalize forward — the walk-forward design would have flagged this overfitting earlier by showing declining OOS performance across folds.

**Combinatorial Purged Cross-Validation (CPCV).** López de Prado's CPCV (2018, *AFML*, Chapter 7; implemented in mlfinlab) provides multiple backtest paths from the same dataset by combinatorially varying which folds are train vs. test. For the operator's use case, CPCV is most valuable for model selection (which GBT regularization or pooling structure generalizes best) rather than for final performance estimation (which should use the held-out chronological test set).

### 3e. The IS/OOS test as diagnostic input

The operator's observation that the descriptive atlas's per-cell argmax "does not generalize forward at any tested smoothness penalty" is strong evidence that the premarket-execution predictive model needs a structurally different approach than the atlas. The specific diagnosis:

1. The atlas fits per-cell optimal exit thresholds to maximize a backward-looking metric (hindsight-optimal bounce). This is a high-variance estimator at small N (30-200 events per cell in many cells), and the per-cell argmax is the epitome of overfitting without regularization.

2. The predictive layer needs: (a) more regularization (hierarchical pooling across cells, not per-cell fitting), (b) different targets (fill probability and post-fill forward bounce, not exit-level argmax), (c) explicit treatment of the non-stationarity (phase regime features, time-to-match-start feature, walk-forward evaluation).

3. The IS/OOS split test on the atlas was run at the **cell-selection** level (which cells have argmax that generalizes?). The predictive-model OOS test is a different question: does the fill-probability and forward-bounce model, trained on the execution features, generalize to held-out events? These are distinct evaluations. The cell-selection IS/OOS failure does not invalidate the execution-model approach; it just confirms that per-cell overfitting is a risk and that pooled/hierarchical models are required.

**Empirical CIs on split design choice.** There is no closed-form CI for split design choices (they are structural, not statistical). The correct validation is: run walk-forward evaluation with purge+embargo, compare OOS metric (e.g., Brier score on fill probability, or information coefficient between predicted and realized forward bounce) across the rolling folds, and check for monotone degradation (non-stationarity signature) vs. variance around a stable mean (random fluctuation signature). Monotone degradation implies the model requires periodic retraining; stable variance implies a single train/val/test split with appropriate purging is sufficient.

### 3f. Summary of recommended split design

| Design choice | Recommended | Rationale |
|---|---|---|
| Unit of splitting | `event_ticker` blocks | Prevents paired-leg leakage (B23 bilateral mechanism) |
| Ordering | Chronological by match_start | Prevents future-data-in-training |
| Purge at boundaries | Yes, T+60min label horizon | Prevents forward-label contamination near cutoff |
| Embargo after boundaries | Yes, 120min (one premarket window) | Prevents autocorrelated-feature leakage |
| Walk-forward folds | Yes, 3-month expanding train + 4-6 week test | Evaluates non-stationarity and robustness |
| Per-category split | No; use global split with category as feature | Cross-category signal sharing; hierarchical model handles category-level heterogeneity |
| CPCV | Yes, for model selection / hyperparameter tuning | Multiple backtest paths reduce selection bias |
| OOS test set | Yes, last 6-8 weeks held out entirely | Final evaluation on data the model has never seen |

---

*References (full citations)*

- Bergault, P., Evangelista, D., Guéant, O., and Vieira, D. (2022). "Closed-form approximations in multi-asset market making." arXiv:1810.04383. https://arxiv.org/abs/1810.04383
- Cartea, Á., Jaimungal, S., and Penalva, J. (2015). *Algorithmic and High-Frequency Trading*. Cambridge University Press. ISBN: 9781107091146.
- Cont, R., Kukanov, A., and Stoikov, S. (2014). "The Price Impact of Order Book Events." *Journal of Financial Econometrics*, 12(1), 47–88. arXiv:1011.6402. https://arxiv.org/abs/1011.6402
- Easley, D., López de Prado, M., and O'Hara, M. (2011/2012). "Flow Toxicity and Liquidity in a High Frequency World." *Review of Financial Studies*, 25(5), 1457–1493. DOI: 10.1093/rfs/hhs053
- Gelman, A., Carlin, J., Stern, H., et al. (2013). *Bayesian Data Analysis*, 3rd ed. CRC Press.
- Hasbrouck, J. (1995). "One Security, Many Markets: Determining the Contributions to Price Discovery." *Journal of Finance*, 50(4), 1175–1199.
- López de Prado, M. (2018). *Advances in Financial Machine Learning*. Wiley. ISBN: 9781119482086.
- Lucchese, L., Pakkanen, M., and Veraart, A. (2023). "The Short-Term Predictability of Returns in Order Book Markets: A Deep Learning Perspective." arXiv:2211.13777. https://arxiv.org/abs/2211.13777
- Niculescu-Mizil, A. and Caruana, R. (2005). "Predicting Good Probabilities With Supervised Learning." *ICML 2005*.
- Pennock, D.M., Debnath, S., Glover, E., and Giles, C.L. (2001). "Modelling Information Incorporation in Markets, with Application to Detecting and Explaining Events." arXiv:1301.0594. https://arxiv.org/abs/1301.0594
- Petajisto, A. (2017). "Inefficiencies in the Pricing of Exchange-Traded Funds." *Financial Analysts Journal*, 73(1), 24–54.
- Rana, R., Nadkarni, V., Moshrefi, N., and Viswanath, P. (2026). "ParlayMarket: Automated Market Making for Parlay-style Joint Contracts." Semantic Scholar. https://www.semanticscholar.org/paper/722bda1229b32ab3f322c31aa1be05d3a527cefc
- Terawong, C. and Cliff, D. (2024). "XGBoost Learning of Dynamic Wager Placement for In-Play Betting on an Agent-Based Model of a Sports Betting Exchange." arXiv:2401.06086. https://arxiv.org/abs/2401.06086
- Wikipedia. (2025). "Purged cross-validation." https://en.wikipedia.org/wiki/Purged_cross-validation
- Zabaljauregui, D. and Campi, L. (2020). "Optimal market making under partial information with general intensities." arXiv:1902.01157. https://arxiv.org/abs/1902.01157
- Zhao, M. and Linetsky, V. (2021). "High frequency automated market making algorithms with adverse selection risk control via reinforcement learning." ACM ICAIF. https://dl.acm.org/doi/10.1145/3490354.3494398
