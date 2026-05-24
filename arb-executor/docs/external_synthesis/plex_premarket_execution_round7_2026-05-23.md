# Plex Premarket Execution Synthesis — Round 7: Premarket Drift Predictors

**Source:** Plex (Perplexity) literature synthesis
**Date:** 2026-05-23
**Prompt context:** Round 7 is upstream literature framing for Path C feature analysis. Path B v3 (HEAD `aef85ee`) measures 28.4% aggregate fill rate across 14,033 atlas N's, with 71.6% miss_fallback still earning only the atlas baseline (9.2% ROI). Within-cell heterogeneity is the residual lever: two worked examples from the same (ATP_MAIN × r85_94 × anchor 91¢) cell show opposite outcomes — `KXATPMATCH-25OCT24SINBUB` (SINBUB: no drift, flat 92¢ at T-4h, Path B miss) vs `KXATPMATCH-25OCT20BERMUN` (BERMUN: massive drift, Munar mid 70¢→90¢, taker fill at 70¢ capturing 21¢ below anchor). Round 7 identifies which T-4h observable features the academic literature predicts should distinguish drift-likely from drift-unlikely events within a given regime cell, so Path C tests the right features rather than fishing across all ~88 columns of the foundation state vector.
**Status:** External synthesis — for integration by chat-side Opus into Path C task design (per-event drift predictor analysis). Per LESSONS C40, external synthesis is committed to repo immediately, not held in chat-side context only.

---

## Sub-Q A — Own-Leg Microstructure Features Predicting Premarket Drift

The within-cell question maps cleanly onto a well-studied problem in market microstructure: given a pre-open or thin-market window, which observables at the *start* of the window predict the *size* of subsequent price movement? The literature addresses spread, volume, flow asymmetry, intensity, and last-traded location as candidate features. Results below are specific to direction of effect on *drift magnitude* toward the anchor (the relevant quantity for bid fill probability), not just volatility.

| Feature | Prediction direction | Effect size | Recommended measurement | Confidence | Literature anchor |
|---|---|---|---|---|---|
| **Initial spread** (yes_ask_close − yes_bid_close at T-4h) | Wide spread → more drift to come (positive correlation with subsequent drift magnitude) | **Moderate** — wide spread signals incomplete price discovery; tight spread signals already-settled price | Absolute spread in cents; percentile-banded within regime; threshold at 3¢ vs ≥5¢ | Well-established (by analogy) | [Cao-Ghysels-Hatheway 2000](https://doi.org/10.1111/0022-1082.00249); [Madhavan-Panchapagesan 2000](https://doi.org/10.1093/RFS/13.3.627) |
| **Initial volume** (volume_in_minute at T-4h, or rolling first-hour sum) | Non-monotone: *low* early volume → price not yet forming → more drift ahead; *high* early volume → informed arrival already underway → directional drift probable but may be partly consumed | **Moderate** — direction reversal at intermediate volume levels; effect is conditional on spread state | Rolling 30-min sum, percentile rank within (category × regime); interaction with spread recommended | Suggestive | [Barclay-Hendershott 2003](https://doi.org/10.1093/rfs/hhg030); [Bacry-Mastromatteo-Muzy 2015](https://doi.org/10.1142/S2382626615500057) |
| **Bid-ask asymmetry** (bid_depth − ask_depth proxy, or bid-side move vs ask-side move in first 30 min) | Bid-side expansion (more depth bid-side, or bid ↑ ahead of ask ↑) predicts upward drift (positive direction); ask-side collapse without bid follow-through predicts flat or reversal | **Moderate** | First-difference of best-bid vs best-ask over T-4h → T-3h; percentile-rank imbalance | Suggestive | [Cont-Kukanov-Stoikov 2014](https://arxiv.org/abs/1011.6402); [Lehalle-Mounjid 2018](https://arxiv.org/abs/1610.00261) |
| **Taker direction asymmetry** (own_taker_flow_in_minute rolling 30 min, net buy vs sell at T-4h) | Net buy taker flow → YES-price rising (price discovery direction = UP); magnitude of taker imbalance predicts subsequent drift magnitude via information share mechanism | **Strong** — taker-side signed flow is the canonical informed-trading channel | EWMA over T-4h → T-3.5h; net_buy / (net_buy + net_sell) ratio; threshold at 0.65+ constituting "imbalanced" | Well-established | [Hasbrouck 1995](https://doi.org/10.1111/j.1540-6261.1995.tb04054.x); [Easley-Lopez de Prado-O'Hara 2012](https://doi.org/10.1093/rfs/hhs019) |
| **Trade-print rate / Hawkes intensity** (count of non-null price_close minutes in T-4h → T-3h, or inter-arrival rate of trades) | High early intensity (many prints, short inter-arrival times) → Hawkes self-excitation predicts sustained activity → MORE drift likely as flow cascade continues | **Moderate** | Count of trade-print minutes in first 60 min post T-4h; exponential decay intensity estimate; rolling 15-min trade count | Suggestive (by analogy) | [Bacry-Mastromatteo-Muzy 2015](https://doi.org/10.1142/S2382626615500057) |
| **Last-traded price vs mid** (price_close − (yes_bid_close + yes_ask_close)/2 at T-4h) | Trade print *below* mid → recent bearish execution → predicts continued downward pressure (negative for YES); trade print *above* mid → recent bullish execution → predicts upward continuation | **Weak–moderate** — signal noisier than taker-flow asymmetry; useful as confirming feature | Raw difference in cents; sign only for binary gate; interaction with taker flow imbalance strengthens signal | Inference | [Cont-Kukanov-Stoikov 2014](https://arxiv.org/abs/1011.6402) |

### A.1 Initial spread as discovery-state indicator

[Cao, Ghysels, and Hatheway (2000)](https://doi.org/10.1111/0022-1082.00249) study Nasdaq pre-open indicative quotes and find that the *width* of the pre-open spread is a direct proxy for how much price discovery remains incomplete: stocks with wide pre-open spreads exhibit larger subsequent convergence moves toward the opening print, because the spread reflects disagreement about fair value rather than settled consensus. This maps directly onto the SINBUB vs BERMUN contrast: SINBUB had a mid of ~92¢ at T-4h with a tight spread (price already near ceiling), leaving almost no room for a further upward move to sweep a 76¢ bid. BERMUN had mid at 70¢ — far below the 91¢ anchor — with a correspondingly wide spread, signaling active disagreement and room for convergence. The Cao et al. finding that "abnormal" pre-open quotes predict subsequent large price adjustments is the strongest upstream support for initial spread as a drift predictor.

[Madhavan and Panchapagesan (2000)](https://doi.org/10.1093/RFS/13.3.627) provide the specialist-pre-open analogue: when indicative quotes are set far from fair value (wide effective spread around fair value), the opening price discovery move is large. For Kalshi favorites, the AMM seed mechanism underprices heavily, and the width of the spread at T-4h proxies for how far the market has already corrected from that seed — tighter spreads indicate correction mostly complete; wider spreads indicate correction still underway.

**Recommended Path C measurement:** `initial_spread_cents = yes_ask_close − yes_bid_close` at the T-4h minute, percentile-banded within the (category × regime) cell. A threshold of ≥5¢ constitutes "wide" for r85_94 favorites (where the typical spread is 2–4¢ at T-4h on already-settled events). Binary gate: wide_spread ∈ {0,1}.

### A.2 Volume: non-monotone relationship with drift

[Barclay and Hendershott (2003)](https://doi.org/10.1093/rfs/hhg030) document that pre-event thin-market periods with *moderate* volume exhibit more price discovery than either silent or high-volume periods: silent periods leave price undiscovered (drift later); high-volume periods have already incorporated most information (drift consumed). For Kalshi premarket windows, very low volume at T-4h signals the market has not yet started converging — predicting more drift ahead — while a volume burst at T-4h signals active flow that may be front-running the convergence, meaning the drift is already in motion.

[Bacry, Mastromatteo, and Muzy (2015)](https://doi.org/10.1142/S2382626615500057) establish that Hawkes-process intensity bursts are self-exciting: elevated trade arrival predicts continued elevated arrival, so early bursts portend sustained flow and larger cumulative drift.

**Recommended Path C measurement:** Rolling 30-minute trade count prior to T-4h vs 30-minute count beginning at T-4h; the *change* in activity rate (acceleration) is the cleaner predictor than level.

### A.3 Taker flow imbalance as the strongest own-leg predictor

[Hasbrouck (1995)](https://doi.org/10.1111/j.1540-6261.1995.tb04054.x) introduces information share as the formal framework linking taker-side signed order flow to price discovery: the venue contributing the largest share of the common efficient-price innovation is the venue where informed traders concentrate. In the Kalshi premarket context, net YES-buying taker flow at T-4h directly predicts upward price movement toward anchor, because taker buys are the mechanism by which informed traders (who know the YES leg is underpriced) push the price up. BERMUN's massive drift was accompanied by aggressive taker buying driving Munar from 70¢ to 90¢ across the window. SINBUB's flat path implies near-balanced taker flow with no net informed direction.

[Easley, López de Prado, and O'Hara (2012)](https://doi.org/10.1093/rfs/hhs019) show that volume-synchronized taker imbalance (VPIN) predicts subsequent price volatility and directional moves by measuring the fraction of informed flow. By analogy to B25 (not direct Kalshi evidence): a rolling 30-minute VPIN-style metric — |net_buy_volume − net_sell_volume| / total_volume at T-4h — is the highest-expected-signal own-leg feature for predicting whether a regime-conditioned bid will be swept.

**Prediction direction is concrete:** High net YES-buy taker flow at T-4h → drift upward → bid below anchor gets swept → fill. High net YES-sell taker flow → price falling → bid might be reached too fast as a taker fill at market (BERMUN scenario) rather than resting maker. Near-zero taker imbalance → SINBUB scenario → no drift, bid never reached.

---

## Sub-Q B — Paired-Leg Features Predicting Drift

Kalshi's paired-binary structure enforces a near-perfect no-arbitrage constraint: YES_fav_price + YES_dog_price ≈ $1.00. Per **B23** doctrine, this bilateral mechanism couples the two legs structurally; any feature measuring the state of this coupling at T-4h is a natural drift predictor for either leg.

| Feature | Prediction direction | Effect size | Recommended measurement | Confidence | Literature anchor |
|---|---|---|---|---|---|
| **Initial paired_arb_gap_maker** (`1.00 − paired_yes_bid_sum` at T-4h) | Large positive gap → structural mispricing → convergence trade likely → drift probable on at least one leg (positive correlation with drift magnitude on whichever leg is underpriced) | **Strong** — the gap IS the no-arb violation; its magnitude measures repricing pressure directly | Raw cents gap; percentile within (category × regime); split by which leg is contributing more to the gap | Well-established (B23 doctrine + ETF-NAV analogy) | [Gatev-Goetzmann-Rouwenhorst 2006](https://doi.org/10.1093/rfs/hhi028); [Ben-David-Franzoni-Moussawi 2018](https://doi.org/10.1111/jofi.12727) |
| **Inter-leg volume asymmetry** (own_volume / partner_volume at T-4h) | Dominant-leg volume (higher activity on one leg) predicts drift on the *lagging* leg toward the dominant leg's price level — information flows from the more-active leg | **Moderate** | Rolling 30-min volume ratio; log(own/partner); threshold at >2× or <0.5× for "asymmetric" | Suggestive | [Hayashi-Yoshida 2005](https://doi.org/10.3150/BJ/1116340299); [Hasbrouck 1995](https://doi.org/10.1111/j.1540-6261.1995.tb04054.x) |
| **paired_yes_bid_sum vs $1.00** (sum of best bids at T-4h) | Bid-sum < $1.00 by large margin → maker-favorable no-arb gap → convergence trade entry opportunity → drift toward $1.00 likely on at least one leg (positive correlation with total paired drift) | **Strong** | Absolute gap: `1.00 − bid_sum`; percentile rank; sign of gap (which side is cheaper) | Well-established (B23 doctrine) | [Avellaneda-Lee 2010](https://doi.org/10.1080/14697680903124632); B23 doctrine |
| **Cross-leg lead-lag at T-4h** (does one leg's price move before the other in the hour T-5h → T-4h?) | Lead leg (the leg showing movement first) predicts subsequent drift direction on both legs — the price discovery information flows from lead to lag | **Moderate** | Hayashi-Yoshida cross-correlation estimate over T-5h → T-4h window; sign of correlation asymmetry; which leg led in the most recent move | Suggestive | [Hayashi-Yoshida 2005](https://doi.org/10.3150/BJ/1116340299); [Hoffmann-Rosenbaum-Yoshida 2013](https://doi.org/10.3150/11-BEJ407) |

### B.1 Paired arb gap as the structural drift pressure metric

The ETF-NAV basis literature provides the clearest analogue. [Ben-David, Franzoni, and Moussawi (2018)](https://doi.org/10.1111/jofi.12727) document that when an ETF trades at a premium or discount to its NAV, the arbitrage pressure to close the gap generates predictable price movements in the underlying basket — and the *magnitude* of the basis predicts the *magnitude* of the subsequent convergence move. The paired-binary setting is a direct structural analogue: `1.00 − paired_yes_bid_sum` is the Kalshi equivalent of the ETF-NAV basis, measuring the no-arb violation at the maker level. When this gap is large at T-4h, the pair is structurally underpriced on both bids combined, and convergence to $1.00 (via drift in one or both legs) is mechanical given any informed participant identifying the gap.

[Gatev, Goetzmann, and Rouwenhorst (2006)](https://doi.org/10.1093/rfs/hhi028) establish that spread *divergence* (distance from equilibrium) is the primary predictor of convergence speed and magnitude in pairs trading: pairs that have diverged more show faster and larger mean-reversion. The `paired_arb_gap_maker` is the Kalshi analog of spread divergence from the $1.00 ceiling. A gap of ≥5¢ at T-4h constitutes a strong divergence signal worth testing as a binary drift-predictor gate.

Per **B23** doctrine, the bilateral mechanism is the structural load-bearer: a bot seeing a large paired gap knows that either the YES-fav or YES-dog price must move toward the no-arb constraint, making the paired gap a feature that predicts drift *on either leg* independently of which leg is currently underpriced. Path C should test: does `paired_arb_gap_maker` at T-4h predict fill_outcome on the favorite leg (YES)?

### B.2 Cross-leg lead-lag and information flow

[Hayashi and Yoshida (2005)](https://doi.org/10.3150/BJ/1116340299) develop an unbiased covariance estimator for non-synchronously trading assets — exactly the setting in Kalshi premarket windows where one leg may have many more trade prints than the other. The Hayashi-Yoshida estimator applied to the 60-minute window T-5h→T-4h yields a cross-leg correlation estimate. A positive correlation with a lead-lag structure (one leg's price at time t correlated with the other's at t+k) identifies the information leader. [Hoffmann, Rosenbaum, and Yoshida (2013)](https://doi.org/10.3150/11-BEJ407) extend this to estimate the lead-lag parameter directly from non-synchronous data.

For Path C, a simpler proxy is available without requiring the full Hayashi-Yoshida estimator: within the T-5h→T-4h hour, which leg had its last price change first? If the favorite leg moved before the underdog leg (or vice versa) in the most recent 5-minute interval, that identifies the current information leader. The lagging leg is predicted to follow, implying drift in the subsequent T-4h→T-20m window.

[Avellaneda and Lee (2010)](https://doi.org/10.1080/14697680903124632) confirm in the equities stat-arb context that inter-security divergences (residuals from a factor model) with high idiosyncratic information content predict stronger mean-reversion; by analogy, a paired binary where one leg leads on information arrival has more residual drift to converge.

---

## Sub-Q C — FV-Anchor Features

FV data (cross-book consensus from Pinnacle and other sportsbooks) is available on approximately 5% of the corpus (post 2026-04-19). Despite the sparsity caveat (per **G19** doctrine, which flags null patterns — here almost all cells will be null-FV), FV is disproportionately useful when present because it provides an external fair value against which Kalshi's current price is directly measured.

| Feature | Prediction direction | Effect size | Recommended measurement | Confidence | Literature anchor |
|---|---|---|---|---|---|
| **Initial fv_delta** (Kalshi last_traded − cross-book FV at T-4h) | Large negative fv_delta (Kalshi cheap vs. FV) → drift UP expected; large positive (Kalshi expensive) → drift DOWN or no additional upward drift | **Strong when FV available** — this is the purest price-efficiency signal; direct cross-venue arbitrage opportunity | Raw cents delta; signed; absolute magnitude as separate feature; percentile rank conditional on FV being available | Well-established | [Hasbrouck 1995](https://doi.org/10.1111/j.1540-6261.1995.tb04054.x); [Tetlock 2008](https://papers.ssrn.com/abstract=929916) |
| **fv_source tier confidence** (pinnacle p1/p2 > aggregate tier-2 > betexplorer) | Higher-tier source → more reliable FV estimate → fv_delta is more trustworthy → stronger drift prediction conditional on same delta magnitude | **Moderate** — tier quality directly proxies FV noise level; noisy FV weakens the delta signal | Ordinal tier: {pinnacle_p1=3, pinnacle_p2=2, aggregate=1, betexplorer=0}; interaction with fv_delta: delta × tier_weight | Suggestive | [Tetlock 2008](https://papers.ssrn.com/abstract=929916); inference from information-share hierarchy |
| **num_books_in_window** | More books → stronger consensus → more reliable FV → drift prediction conditional on FV has higher confidence | **Moderate** — weak when only one book available; strong when 3+ books agree | Count of books contributing to FV; binary gate: ≥3 books vs <3 | Suggestive | [Tetlock 2008](https://papers.ssrn.com/abstract=929916) |
| **FV-conditioned magnitude scaling** | When FV available and fv_delta > threshold, Round 5's multiplicative-confidence-weight finding applies: FV should scale bid aggressiveness, not replace it. Integration: drift_score_base × fv_multiplier | **Conditional strong** — at 5% presence, FV will not dominate the overall predictor; its role is as a high-confidence override when available | Multiplicative gate: if FV available, weight drift_probability upward by |fv_delta|/10; graceful degradation otherwise per Round 5 | Inference (builds on Round 5) | Round 5 (`plex_premarket_execution_round5_2026-05-23.md`); [Hasbrouck 1995](https://doi.org/10.1111/j.1540-6261.1995.tb04054.x) |

### C.1 fv_delta as the gold-standard drift predictor

[Tetlock (2008)](https://papers.ssrn.com/abstract=929916) directly finds that prediction market prices are inefficient relative to external consensus signals — markets that are informationally thin (low liquidity) show slower incorporation of public information and allow cross-venue arbitrage to persist longer. This validates the use of cross-book FV as a lead indicator for Kalshi prices: when Pinnacle (a sharp-money sportsbook that closes early against informed bettors) prices Munar at 85¢ while Kalshi is still at 70¢, the 15¢ gap is a direct prediction that Kalshi will drift toward 85¢.

[Hasbrouck (1995)](https://doi.org/10.1111/j.1540-6261.1995.tb04054.x) information share formalizes this: in a multi-venue setting, the venue with higher information share (sharper price discovery) leads price formation, and the lagging venue drifts toward the leader. For Kalshi vs Pinnacle, Pinnacle is almost certainly the information leader for any match where both venues trade — Pinnacle's professional bettors and early-limit-raise mechanism incorporate fundamental information faster than Kalshi's retail-dominated order flow.

**Sparsity caveat:** At ~5% corpus presence, fv_delta will be missing for ~95% of Path C test events. The correct Path C design is: (1) measure fv_delta effects within the 5% FV-available subset as a validation dataset for the FV-based predictor, and (2) use the other features (Sub-Q A and B) as the primary drift predictors across all 14,033 events. Per [Ghysels' MIDAS framework](https://rady.ucsd.edu/_files/faculty-research/valkanov/midas-touch.pdf) (mixed-data sampling for mixed-frequency data), a mixed regression that combines sparse FV-delta when available with always-available microstructure features is the statistically sound approach — do not impute FV or treat absence as fv_delta=0.

### C.2 FV-source tier weighting integrates Round 5's multiplicative finding

Round 5 (`plex_premarket_execution_round5_2026-05-23.md`) established that FV is best deployed as a multiplicative confidence weight on aggressiveness, gracefully degrading at 96.5% absence. Round 7 refines: when FV is available, the appropriate magnitude scaling for drift prediction is `|fv_delta_cents| / typical_regime_spread`, where typical_regime_spread is the corpus mean bid-ask spread for the (category × regime) cell. This normalizes the FV signal to be comparable across regimes. A Pinnacle-sourced fv_delta of 15¢ on a r85_94 event (where the typical spread is 3¢) is a 5× spread signal — very strong. The same 15¢ delta on a r45_54 event (where the typical spread might be 6¢) is a 2.5× signal — moderate.

---

## Sub-Q D — Metadata Features

Metadata features require no microstructure data and are available for all events at T-4h or earlier. Their predictive value for drift comes not from real-time market state but from population-level patterns that predict *which events are more likely to have informative premarket flow arrive*.

| Feature | Prediction direction | Effect size | Recommended measurement | Confidence | Literature anchor |
|---|---|---|---|---|---|
| **Time of day / day of week** | Late-morning to early-afternoon match times (UTC) → more time for sharp-money to arrive before T-4h → price likely already discovered → LESS drift at T-4h; very early morning or late evening matches → less activity window → more drift remaining | **Weak** — effect documented in sportsbook literature but likely weak on Kalshi where the market-time is the constant; however, match-start time relative to Pinnacle market-open is relevant | Hours between match start and Pinnacle's typical line-release (≥24h = well-established market); day of week (weekday vs weekend for data coverage) | Suggestive | [Croxson-Reade 2014](https://doi.org/10.1111/ecoj.12055); [Levitt 2004](https://doi.org/10.1086/422583) |
| **Tournament tier / round** (Grand Slam vs ATP 1000 vs Challenger; early round vs QF/SF) | High-profile match → sharper money arrived earlier → price more settled at T-4h → LESS drift remaining; Challenger early rounds → fewer informed bettors → MORE drift remaining | **Moderate** — tournament tier is a reliable proxy for market depth and informed-money concentration | Ordinal tier: {GS=4, Masters=3, 500=2, 250=1, Challenger=0}; round: {F=5, SF=4, QF=3, R16=2, R32=1}; ATP_MAIN vs ATP_CHALL already in category | Suggestive | [Forrest-Goddard-Simmons 2005](https://doi.org/10.1016/j.ijforecast.2005.03.002); [Paul-Weinbach 2007](https://www.ubplj.org/index.php/jpm/article/view/429) |
| **Ranking gap proxy beyond anchor regime** | Extreme ranking gap (e.g., top-5 vs unranked) → match outcome near-certain → less room for information-based price movement beyond AMM seeding → less drift; close-ranked matches → more uncertainty → more arrival of new information → more drift potential | **Weak–moderate** — anchor regime already captures ranking proxy; incremental gain from explicit ranking gap depends on within-regime variation in actual rankings | Raw ranking differential (r1 − r2 absolute); log ratio; head-to-head recent win% as alternative proxy; surface-specific ELO if available in corpus | Inference | [Levitt 2004](https://doi.org/10.1086/422583); [Forrest-Goddard-Simmons 2005](https://doi.org/10.1016/j.ijforecast.2005.03.002) |

### D.1 Time-of-day and tournament context

[Croxson and Reade (2014)](https://doi.org/10.1111/ecoj.12055) study Betfair in-play soccer betting and document that information arrival rates vary sharply with match timing — premarket price discovery accelerates as match time approaches and as more observers have formed opinions. For Kalshi tennis, the analogous effect is that matches with long advance notice (Grand Slams scheduled days ahead) have more premarket discovery time, meaning the T-4h price is more likely to be already near fair value and less likely to drift further.

[Levitt (2004)](https://doi.org/10.1086/422583) establishes that sportsbooks set non-balanced prices to exploit bettor biases, and that sharp money corrects these biases — but the *timing* of sharp-money correction depends on market-open schedules. Pinnacle typically raises limits on ATP Grand Slam matches 72+ hours before match start, while Challenger matches often open within 24 hours. This means that at T-4h, a Grand Slam favorite's Kalshi price is more likely to have already incorporated sharp-money convergence than a same-anchor Challenger favorite. The drift remaining at T-4h is therefore *negatively* correlated with tournament tier.

**Prediction direction for drift magnitude:** GrandSlam/Masters → lower residual drift → Path B bid less likely to fill; Challenger early-round → higher residual drift → bid more likely to fill. This is the opposite of the volume story but consistent with market-depth reasoning. The BERMUN event (ATP_MAIN, presumably a lower-tier ATP match based on the October 2025 timing and Munar's ranking) is consistent with the Challenger/lower-tier effect: less sharp-money saturation at T-4h left room for the 20¢ drift.

### D.2 Ranking gap and incremental value beyond anchor

The anchor regime (r85_94 for both SINBUB and BERMUN) already encodes the baseline probability estimate. The question for Path C is whether there is *additional* predictive value from the exact underlying ranking gap, net of the regime. By analogy to [Forrest, Goddard, and Simmons (2005)](https://doi.org/10.1016/j.ijforecast.2005.03.002), who find that bookmakers' odds contain more information than statistical models because they incorporate non-public information about player form and conditions: the within-regime spread of anchor prices (e.g., 85¢ vs 94¢ within r85_94) may proxy for whether the ranking gap is truly extreme or borderline. Path C can test this by interacting `anchor_price` (as a continuous variable within the regime cell) with drift outcome — if 94¢ events (near-certain outcomes) show less drift than 85¢ events (merely strong favorites), the anchor itself captures the ranking information and no separate ranking feature is needed.

---

## Sub-Q E — Multi-Feature Integration Framework

Once Sub-Qs A–D produce a candidate feature list, the question is how to combine them into a per-event drift-likelihood score that is (a) predictive out of sample and (b) deployable without requiring continuous retraining.

### E.1 Recommended model classes in priority order

**Rule-based gates (Day 1 deployable, no training required).** The clearest literature verdict is that rule-based composite gates — two or three features combined with AND logic — are robust when the feature list is short and the mechanism is well-grounded. Round 4's composite-event detector (`plex_premarket_execution_round4_2026-05-22.md`) established exactly this architecture for burst detection: two-of-four conditions sufficient to trigger action. For per-event drift prediction, a similar gate is the right starting point:

*Candidate Rule-1:* `IF (initial_spread_cents ≥ 5) AND (taker_imbalance_30min > 0.60) THEN drift_likely`

*Candidate Rule-2:* `IF (paired_arb_gap_maker ≥ 5¢) AND (inter_leg_volume_asymmetry > 2.0) THEN drift_likely`

Rule-based gates are interpretable, have no false precision, and fail gracefully to the unconditional regime-cell estimate when the gate is not triggered.

**Logistic regression (next step, ≥100 training events per regime cell required).** Round 2 (`plex_premarket_execution_round2_2026-05-21.md`) established logistic regression as the first modeling step for execution feature importance. For per-event drift prediction, a logistic model on {initial_spread, taker_imbalance, paired_arb_gap, time_to_match, tournament_tier} provides calibrated probabilities and interpretable coefficients. Its main advantage is that it produces P(drift_reaches_bid) rather than a binary label, which feeds directly into the bid-aggressiveness calculation: `bid_offset ≈ f(drift_probability, expected_drift_magnitude)`.

**GBT (shallow, ≥1,000 training events for stable estimates).** Per Round 2, gradient-boosted trees capture non-linear interactions (e.g., `spread × tournament_tier` or `taker_imbalance × paired_gap`) that logistic regression misses. The key constraint for the 10-month corpus (~14,000 events, ~6,000 per ATP_MAIN × favorite regime) is that enough within-cell events are available to train without severe overfitting. At 14,033 total events and ~36 regime cells, the average cell has ~390 events — borderline for GBT with more than 3–4 features. Recommend GBT only if path C confirms ≥500 events per cell after filtering for T-4h data completeness.

### E.2 Signal-driven execution integration with Cartea-Bank-Körber 2024

Round 5 established [Bank, Cartea, and Körber (2024)](https://arxiv.org/abs/2306.00621) as the primary anchor for signal-driven execution: their framework shows that when a short-term signal (observable at the placement decision) predicts imminent order flow changes, the optimal response is not to adjust the bid level but to adjust *when* to be in the market. The Round 7 extension: if the T-4h drift-likelihood score exceeds a threshold, the bot should post *earlier* or more aggressively (smaller offset, higher fill probability); if below threshold, the bot should post *later* or skip the active bid entirely and fall back to the T-20m taker.

The Cartea-Bank-Körber framework specifically addresses the case where signals are observable at T-4h but the terminal action extends over hours — they show that early-signal placement dominates late entry when the signal has predictive half-life longer than the placement window. For T-4h drift predictors where the prediction horizon is ~3.5 hours, the signal must be predictive over that horizon — not just the next 15 minutes. Whether T-4h microstructure features have that persistence is the empirical question Path C should answer first.

### E.3 Validation discipline for a per-event drift predictor

Round 2 established purged+embargoed+CPCV ([López de Prado, 2018](https://www.wiley.com/en-us/Advances+in+Financial+Machine+Learning-p-9781119482086)) as the canonical protocol. Refinements for a per-event drift predictor specifically:

1. **Event-block splits, chronological.** Never randomize — the test set must be strictly after the train set to prevent leakage from serial correlation in match scheduling.

2. **Stratified by (category × regime).** Preserve regime proportions across folds; without stratification, rare regimes (r05_14) may be absent from test sets.

3. **Purge window of ±1 tournament block.** Events from the same tournament share surface, conditions, and player form; purge the same tournament-week from the train set when it appears in the test set.

4. **Embargo of 2 weeks.** Weekly tournament cycles mean correlated events persist for ~2 weeks; embargo at that boundary.

5. **Target variable:** Binary `fill_or_not` for classification; continuous `drift_magnitude = anchor_price − min(price_close over T-4h→T-20m)` for regression — this is the margin the bid needs to be reached.

### E.4 Overfitting mitigation specific to this corpus

The corpus covers 10 months (August 2025–May 2026). A T-4h feature predictor trained on this data faces several overfitting risks unique to the domain:

**Season-specific pattern leakage.** The 2025–2026 ATP season has specific structural features (Sinner's dominance, surface conditions, scheduling anomalies) that may not replicate in 2026–2027. [López de Prado's AFML Chapter 8](https://www.wiley.com/en-us/Advances+in+Financial+Machine+Learning-p-9781119482086) on backtest overfitting documents that a model trained on any finite sample of market data will exhibit spurious feature importances for season-specific correlations. Mitigation: prefer low-complexity models (logistic, shallow GBT with max_depth=3) that cannot memorize specific matches; avoid features with high cardinality (raw player IDs, exact ranking values) that allow the model to learn player-specific patterns rather than structural microstructure patterns.

**Feature substitution effects.** [López de Prado (2020)](https://ssrn.com/abstract=3517595) documents that correlated features generate MDI/MDA importances that are split between redundant features, making both appear unimportant when either is individually strong. For the proposed feature list (spread, taker_imbalance, paired_gap, tournament_tier), the taker_imbalance and spread features will be correlated — spread is partly endogenous to whether informed flow is arriving. Use Single Feature Importance (SFI) to test each feature independently before building the multivariate model, and apply clustered feature importance to group correlated features before selecting.

**10-month deployment generalization concern.** The model will be trained on corpus data ending May 2026 and deployed from June 2026 forward. Market structure may shift (Kalshi platform changes, new market participants, ATP season transition). Recommend: set aside the most recent 2 months (March–May 2026) as a holdout validation set that is never used in CPCV; use CPCV only on the August 2025–February 2026 window; deploy only if holdout validation confirms out-of-sample performance. This creates a temporal buffer between training and live deployment.

---

## Path C Priority Order: Recommended Feature Testing Sequence

Based on Sub-Qs A–D, the following ordering reflects expected signal strength × measurement feasibility × independence from other features.

**Tier 1 — High expected signal, always available, low measurement complexity. Test these first.**

1. **Taker direction asymmetry at T-4h** (`own_taker_flow_in_minute`, 30-min rolling net balance). Strongest theoretical anchor (Hasbrouck information share, VPIN). Binary: |net_buy_fraction − 0.5| > 0.15. Corpus-testable immediately from premarket_tape_v1.
2. **Initial paired_arb_gap_maker** (`1.00 − paired_yes_bid_sum` at T-4h). Structural B23 feature, mechanically related to convergence requirement. Directly available in premarket tape. Threshold: ≥5¢ gap.
3. **Initial spread** (`yes_ask_close − yes_bid_close` at T-4h). Simplest microstructure feature; proxies for price-discovery completeness. Percentile-banded within regime. Directly available.

**Tier 2 — Moderate expected signal, require slightly more feature engineering. Test second.**

4. **Volume acceleration** (30-min count T-4h→T-3.5h vs prior 30-min count). Non-monotone effect; self-exciting via Hawkes. Requires computing delta-volume from premarket tape.
5. **Tournament tier** (ATP_MAIN vs ATP_CHALL already captured; refine with {GS, Masters, 500, 250, Challenger} from event metadata). Metadata, available for all events.
6. **Bid-ask asymmetry direction** (which of bid or ask moved first in T-4.5h→T-4h). Requires per-leg BBO history near T-4h window.

**Tier 3 — Lower expected marginal signal given Tier 1 and 2, or harder to measure reliably. Test last or condition on data availability.**

7. **Cross-leg lead-lag** (Hayashi-Yoshida or simplified proxy). Requires paired leg data; more computation; moderate expected signal given paired_arb_gap already captures the structural coupling.
8. **Last-traded price vs mid** at T-4h. Weak independent signal; likely captured by spread + taker_flow.
9. **FV-delta** when available. Test on the ~5% FV-available subset as a separate validation. High signal when present; ignore when absent.

**Validation discipline summary:** CPCV with N=8 folds, k=2 test folds, chronological ordering, 2-week embargo, tournament-block purge. Start with logistic regression as interpretability baseline; promote to GBT only if logistic AUC < 0.62 on holdout. Report feature importances using SFI (single feature importance per [López de Prado 2018](https://www.wiley.com/en-us/Advances+in+Financial+Machine+Learning-p-9781119482086)) before building multivariate models, to isolate individual signals before testing interactions.

**The concrete corpus-testable starting point:** Measure `drift_reached_bid = (min(price_close over T-4h→T-20m) ≤ bid_target)` for all fill-outcome rows. Regress this binary label on `initial_spread_cents`, `taker_imbalance_30min`, and `paired_arb_gap_cents`, with (category × regime) fixed effects, using the purged CPCV protocol above. This is a 3-feature logistic model on the full 14,033-event corpus — it will produce AUC, feature coefficients, and calibrated P(drift_reaches_bid) as the Path C Phase 1 output. Whether any feature has AUC lift over the regime-cell base rate determines whether Path C's conditional placement refinement is worth implementing.

---

## Provenance — Citations

| # | Work | Authors | Year | Full URL |
|---|------|---------|------|----------|
| 1 | Price Discovery without Trading: Evidence from the Nasdaq Pre-opening | Cao, C.; Ghysels, E.; Hatheway, F. | 2000 | https://doi.org/10.1111/0022-1082.00249 |
| 2 | Price Discovery in Auction Markets: A Look Inside the Black Box | Madhavan, A.; Panchapagesan, V. | 2000 | https://doi.org/10.1093/RFS/13.3.627 |
| 3 | Price Discovery and Trading After Hours | Barclay, M.; Hendershott, T. | 2003 | https://doi.org/10.1093/rfs/hhg030 |
| 4 | The Price Impact of Order Book Events | Cont, R.; Kukanov, A.; Stoikov, S. | 2014 | https://arxiv.org/abs/1011.6402 |
| 5 | Limit Order Strategic Placement with Adverse Selection Risk | Lehalle, C.-A.; Mounjid, O. | 2018 | https://arxiv.org/abs/1610.00261 |
| 6 | One Security, Many Markets: Determining the Contributions to Price Discovery | Hasbrouck, J. | 1995 | https://doi.org/10.1111/j.1540-6261.1995.tb04054.x |
| 7 | Flow Toxicity and Liquidity in a High Frequency World (VPIN) | Easley, D.; López de Prado, M.; O'Hara, M. | 2012 | https://doi.org/10.1093/rfs/hhs019 |
| 8 | Hawkes Processes in Finance | Bacry, E.; Mastromatteo, I.; Muzy, J. | 2015 | https://doi.org/10.1142/S2382626615500057 |
| 9 | Pairs Trading: Performance of a Relative-Value Arbitrage Rule | Gatev, E.; Goetzmann, W.; Rouwenhorst, K. | 2006 | https://doi.org/10.1093/rfs/hhi028 |
| 10 | Statistical Arbitrage in the U.S. Equities Market | Avellaneda, M.; Lee, J.-H. | 2010 | https://doi.org/10.1080/14697680903124632 |
| 11 | On Covariance Estimation of Non-Synchronously Observed Diffusion Processes | Hayashi, T.; Yoshida, N. | 2005 | https://doi.org/10.3150/BJ/1116340299 |
| 12 | Estimation of the Lead-Lag Parameter from Non-Synchronous Data | Hoffmann, M.; Rosenbaum, M.; Yoshida, N. | 2013 | https://doi.org/10.3150/11-BEJ407 |
| 13 | Do ETFs Increase Volatility? (ETF-NAV arbitrage basis) | Ben-David, I.; Franzoni, F.; Moussawi, R. | 2018 | https://doi.org/10.1111/jofi.12727 |
| 14 | Liquidity and Prediction Market Efficiency | Tetlock, P. | 2008 | https://papers.ssrn.com/abstract=929916 |
| 15 | The MIDAS Touch: Mixed Data Sampling Regression Models | Ghysels, E.; Santa-Clara, P.; Valkanov, R. | 2004 | https://rady.ucsd.edu/_files/faculty-research/valkanov/midas-touch.pdf |
| 16 | Why Are Gambling Markets Organized So Differently from Financial Markets? | Levitt, S. | 2004 | https://doi.org/10.1086/422583 |
| 17 | Information and Efficiency: Goal Arrival in Soccer Betting | Croxson, K.; Reade, J. | 2014 | https://doi.org/10.1111/ecoj.12055 |
| 18 | Odds-Setters as Forecasters: The Case of English Football | Forrest, D.; Goddard, J.; Simmons, R. | 2005 | https://doi.org/10.1016/j.ijforecast.2005.03.002 |
| 19 | Does Sportsbook.com Set Pointspreads to Maximize Profits? | Paul, R.; Weinbach, A. | 2007 | https://www.ubplj.org/index.php/jpm/article/view/429 |
| 20 | Optimal Execution and Speculation with Trade Signals | Bank, P.; Cartea, Á.; Körber, L. | 2024 | https://arxiv.org/abs/2306.00621 |
| 21 | Advances in Financial Machine Learning | López de Prado, M. | 2018 | https://www.wiley.com/en-us/Advances+in+Financial+Machine+Learning-p-9781119482086 |
| 22 | Reinforcement Learning for Optimized Trade Execution | Nevmyvaka, Y.; Feng, Y.; Kearns, M. | 2006 | https://dl.acm.org/doi/10.1145/1143844.1143929 |
| 23 | A Reinforcement Learning Extension to the Almgren-Chriss Framework | Hendricks, D.; Wilcox, D. | 2014 | https://doi.org/10.1109/CIFEr.2014.6924109 |
| 24 | Clustered Feature Importance | López de Prado, M. | 2020 | https://ssrn.com/abstract=3517595 |
| 25 | Price Discovery and Trading in Modern Prediction Markets | (Recent 2025 SSRN) | 2025 | https://papers.ssrn.com/sol3/Delivery.cfm/5331995.pdf?abstractid=5331995 |

**Cross-references to prior rounds (do not re-derive):**
- Round 1 (`plex_premarket_execution_round1_2026-05-21.md`): paired binary structure, cross-book consensus, Hasbrouck information share foundation
- Round 2 (`plex_premarket_execution_round2_2026-05-21.md`): CPCV purged+embargoed validation, GBT feature importance, logistic baseline, event-block chronological splits — **directly extended by Sub-Q E.3**
- Round 4 (`plex_premarket_execution_round4_2026-05-22.md`): composite-event detector (two-of-four architecture) — **directly extended by Sub-Q E.1 rule-based gates**
- Round 5 (`plex_premarket_execution_round5_2026-05-23.md`): Cartea-Bank-Körber 2024 signal-driven execution, FV multiplicative confidence weight, velocity-conditional cross-fallback — **directly extended by Sub-Qs C and E.2**
- Round 6 (`plex_premarket_execution_round6_2026-05-23.md`): Path B deployment realism, fill rate measurement, staged deployment — **empirical context that motivates Round 7**

**Doctrine codes engaged:**
- **B23** (paired-leg bilateral mechanism): Sub-Q B load-bearing; paired_arb_gap_maker is the B23 structural feature; inter-leg volume asymmetry and bid-sum features directly derive from B23
- **B25** (minute-cadence simulator overstatement): not directly re-derived; applies to any fill-rate estimate from Path C corpus testing
- **F33** (depth-chain data gap): Sub-Q A taker-flow features rely on volume data; F33 cautions that volume_in_minute series may have null gaps that require handling before computing rolling taker_imbalance
- **G19** (candle null patterns): Sub-Q C FV sparsity caveat — ~95% of fv_delta is null; do not impute zero; use mixed-frequency approach per Ghysels MIDAS
- **A39** (cents-vs-ROI asymmetry): Path C's goal is to convert conditional drift predictions into adjusted bid offsets; a 2¢ improvement in expected_improvement_cents translates to +20pp ROI at 10¢ position sizing
- **G22** (three-axis deployment math): Path C's conditional placement output feeds Axis 2 (entry-side improvement); successful predictor increases fill rate and/or expected discount on the filled fraction, multiplying against the existing atlas exit (Axis 3) benefit
