# Plex Premarket Execution Synthesis — Round 1: Paired Binary Markets, Premarket Discovery, Cross-Book Consensus, Maker vs. Alpha-Capture

**Source:** Plex (Perplexity) literature synthesis
**Date:** 2026-05-21
**Prompt context:** Round 1 was asked to synthesize literature across four sub-questions relevant to the Kalshi tennis binary premarket-execution policy layer: (1) market-making and maker-bid placement in paired binary contracts with a known no-arb sum constraint; (2) premarket/pregame price discovery dynamics in binary or fixed-odds markets — how spreads, depth, and consensus-vs-local gaps evolve as time-to-event-start decreases; (3) cross-book consensus (Pinnacle + tier-2 books) as a predictive signal for short-horizon price convergence in less-liquid venues; and (4) the distinction between true market-making and alpha capture via maker placement, with emphasis on directional-thesis passive execution and its separation from the indifference-to-direction posture of canonical market-making.
**Status:** External synthesis — for integration by chat-side Opus into the U4 Phase 3 build and bid-laying policy spec. Per LESSONS C40, external synthesis is committed to repo immediately, not held in chat-side context only.

---

## 1. Market-Making and Maker-Bid Placement in Paired Binary Contracts with a No-Arb Sum Constraint

### 1a. The structural uniqueness of sum-to-$1 paired binaries

The Kalshi tennis paired structure — player1-YES and player2-YES summing to 100¢ by no-arb identity — is not well-studied as a distinct object in the microstructure literature. The closest structural analogs are (i) put-call parity in options markets, (ii) complementary event binary markets in prediction-market literature, and (iii) compositional asset pairs in ETF-NAV and index-futures settings. Each provides partial insight; none maps perfectly.

**Options-pair parity analogy.** In options markets, a European call and put at the same strike and expiration satisfy C − P = S − Ke^{−rT}, and violations are closed by market-makers who simultaneously leg both sides. Academic work on put-call parity enforcement (Garleanu and Pedersen 2011, "Margin-Based Asset Pricing and Deviations from the Law of One Price," *Review of Financial Studies*, https://doi.org/10.1093/rfs/hhr027) demonstrates that the parity spread is mean-reverting when capital is not constrained and that temporary violations correlate with cross-market liquidity imbalances. By inferential analogy to the Kalshi structure, the `paired_arb_gap_maker = 1.00 − paired_yes_bid_sum` is structurally the same as a momentary put-call parity violation: both legs' bids sum to less than $1.00, meaning a patient bidder resting on both sides would capture the gap if filled. The critical difference: options parity violations carry no-fill-uncertainty risk only if the underlying is illiquid; in the Kalshi structure, the fills on the two legs are independent — you may get filled on one without the other, creating an unclosed one-leg position (inference from parity literature, not a direct empirical result from Kalshi-specific data).

**ParlayMarket and combinatorial prediction market AMM research.** Rana, Nadkarni, Moshrefi, and Viswanath (2026, "ParlayMarket: Automated Market Making for Parlay-style Joint Contracts," SSRN/Semantic Scholar, https://www.semanticscholar.org/paper/722bda1229b32ab3f322c31aa1be05d3a527cefc) demonstrate that when correlated or logically-linked binary contracts are traded independently, AMM pricing can diverge from the coherent joint distribution, creating persistent cross-leg distortions. Their convergence theorem — that repeated trading drives an AMM toward the best approximation of the true joint distribution — implies the converse: a single-venue binary market like Kalshi with limited liquidity will transiently depart from the coherent joint distribution whenever information or order flow is asymmetric across legs. This provides formal grounding for the `paired_mid_sum` deviation from $1 as a microstructure-stress indicator (cross-reference: the `paired_arb_gap_maker` and `paired_arb_gap_taker` features in the per_minute_features.parquet schema, E12 premarket phases).

**Sum-constrained binary market structure.** Brahma, Das, and Magdon-Ismail (2010, "Comparing Prediction Market Structures, With an Application to Market Making," arXiv:1009.1446, https://arxiv.org/abs/1009.1446) compare LMSR and Bayesian market makers in prediction markets, finding that market makers face a fundamental tradeoff: adaptability to sudden shocks (like a sharp Pinnacle move) versus convergence stability. For a paired-binary operator who is not providing two-sided liquidity (no YES + NO quoting per leg), this tradeoff manifests differently: the operator quotes bids on one side only (maker-buy), so adaptability is expressed purely through bid price adjustment and cancellation timing (C37 pre-replace gate), not through spread management.

**Closed-form approximations for multi-asset market making.** Bergault, Evangelista, Guéant, and Vieira (2022, "Closed-form approximations in multi-asset market making," *SIAM Journal on Financial Mathematics*, arXiv:1810.04383, https://arxiv.org/abs/1810.04383) extend the Avellaneda-Stoikov framework to correlated asset pairs. Their key insight: when two assets are correlated, the optimal market-making quotes on each leg are functions of the joint inventory position, not just the single-leg inventory. By analogy (inferential bridge — the operator is not market-making in the two-sided sense), when both legs of the same event are simultaneously bid, the fill risk on each leg is correlated with the information shock that would cause the other leg to move. This motivates monitoring `partner_yes_bid_close` and `partner_taker_flow_in_minute` as co-risk indicators even when placing bids only on one leg.

### 1b. Specific prediction-market maker-quoting literature

Groeger (2016, "The Informational Content of the Limit Order Book: An Empirical Study of Prediction Markets," arXiv:1609.03471, https://arxiv.org/abs/1609.03471) studies binary option prediction markets and finds that limit order books in these venues contain significant predictive information — specifically, that imbalance between the buy-side and sell-side queues at the best price is a reliable short-horizon predictor of price direction. The finding is directly relevant: the per-minute `bid_consumption_velocity` and `ask_consumption_velocity` behavioral depth proxies in the corpus are empirical proxies for exactly this queue imbalance. Groeger also finds that in these markets, the LOB imbalance signal decays faster than in equity markets, consistent with the lower liquidity and higher event-risk in binary outcomes. He reports "little evidence for convergence" in some market subsets, which is consistent with the operator's observation that Kalshi tennis markets are not persistently efficient (A39 cents-vs-ROI geometry).

The relevant gap in the literature is that no academic work directly studies Kalshi tennis market microstructure as of 2026, nor the specific interaction of paired-leg sum constraints in event-linked binary CDA markets. The closest in spirit is Nechepurenko (2026, "Resolution-Aware Perpetual Futures on Binary Prediction Markets," Semantic Scholar, https://www.semanticscholar.org/paper/18375b082ac7ea58e1ab560dec571beaeb45e9b1), which develops risk-design frameworks for instruments whose underlying is a binary prediction-market probability and identifies specific non-portability of standard financial tools — particularly that boundary-aware behavior near terminal resolution (0 or 1) requires dedicated treatment. This is relevant to B14/G17 premarket vs. in-match decomposition: features and signals that are predictive during formation and stable premarket phases may fail near the pregame phase if the market is approaching a resolution-proximity regime.

---

## 2. Premarket / Pregame Price Discovery Dynamics in Binary or Fixed-Odds Markets

### 2a. Phase structure of premarket in sports and prediction markets

The practitioner observation that premarket activity follows three phases — formation (sparse activity, wide spreads), stable (midmarket consolidates), pregame (tightening, late sharp money, line moves) — finds empirical support in adjacent literatures, though no paper directly studies Kalshi tennis at minute resolution.

**Betfair exchange in-play and pre-match dynamics.** The most directly applicable empirical work is the University of Reading discussion paper on informational efficiency in Betfair EPL markets (Reade et al. 2019/20, "Informational efficiency and behaviour within in-play prediction markets," https://www.reading.ac.uk/web/files/economics/emdp201920.pdf). Key documented findings: (a) Pre-match prices show a statistically significant reverse favourite-longshot bias (favourite bias): favorites are consistently overpriced pre-match relative to their actual win rate, while longshots are underpriced. For home odds, the underpriced range is implied probability below 0.24; for away odds, below 0.14. (b) A simple betting strategy that exploits pre-match underpriced odds generates 40-56% gross ROI in-sample and 51.9% out-of-sample — consistent with Kalshi's systematic opportunity structure identified in the atlas (A39). (c) After major in-game events (goals), mispricing is strongest approximately 20 seconds after the event and can persist up to five minutes — showing that even in a relatively liquid prediction market, price discovery is gradual and behaviorally biased.

By inferential analogy to the Kalshi tennis structure, the formation/stable/pregame decomposition (E12 premarket phases) maps to: formation ≈ match announced, early quotes set by few informed traders; stable ≈ multiple sportsbooks + Kalshi agree on a consensus range; pregame ≈ Pinnacle and tier-2 books have absorbed late sharp information, spreads tighten at Kalshi, last few minutes before match start where `time_to_match_start_min` approaches 0.

**NFL/NBA pre-game line movement research.** Levitt (2004, "Why Are Gambling Markets Organised Differently from Financial Markets?," *Journal of Economic Perspectives*) argues that sportsbooks do not behave as pure Bayesian price-setters responding to information — they also shade lines toward positions that equalize book exposure, creating systematic biases. This is structurally relevant: if Kalshi prices are partly influenced by retail flow rather than pure FV discovery, the consensus_fv from Pinnacle (which Levitt and subsequent work establishes as a sharp-money-accepting anchor) will systematically diverge from Kalshi, and the fv_delta signal will be driven partly by this distributional difference, not only by idiosyncratic mispricing.

Avery and Chevalier (1999, "Identifying Investor Sentiment from Price Paths: The Case of Football Betting," *Journal of Business*) document that NFL betting lines move in response to informed bettors with demonstrated track records, and that later-arriving information is incorporated faster. This supports the inference that at Kalshi, the pregame phase (last 20-60 minutes before match start) is the period where sharp information from Pinnacle's line has already been set but may not yet be fully reflected in Kalshi's local BBO — exactly the window the atlas T-20m anchor is designed to capture (A35 match-start signal).

**Betfair horse racing and soccer exchange literature.** Tondapu (2024, "Efficient Market Dynamics: Unraveling Informational Efficiency in UK Horse Racing Betting Markets Through Betfair's Time Series Analysis," arXiv:2402.02623, https://arxiv.org/abs/2402.02623) finds that Betfair horse racing betting returns show remarkably high informational efficiency — light tails, quickly fading autocorrelations, and absence of long-term memory. This contrasts with the Reade et al. Betfair EPL findings, suggesting that efficiency varies substantially by sport (liquidity, bettor sophistication, information availability). Tennis on Kalshi — a less-liquid venue with a smaller pool of informed participants than major Betfair sports — is likely to exhibit lower efficiency than Betfair horse racing and comparable or lower efficiency than Betfair EPL. This supports the operator's position that persistent, atlas-calibrated mispricings are real (B25 minute-cadence evidence; G22 three-axis math).

### 2b. Spread and depth dynamics approaching match start

The most robust empirical pattern in cross-market price discovery literature is that bid-ask spreads narrow and depth at the BBO increases as markets approach informational consensus. In thin markets, the dynamics are reversed in one respect: the arrival of a single large informed participant (one sharp-money bet at Pinnacle, one Kalshi taker print) can cause a step-change rather than continuous convergence. For the operator's use case, this means:

- During formation phase, `paired_arb_gap_maker` is largest (both legs' bids are far from midmarket, sum much less than $1.00) — maker bids placed here achieve the best prices but face longest fill waits and highest exposure to information arriving later.
- During stable phase, the arb gap narrows as more bids enter the book; `consensus_fv` and local BBO are closer together; the `fv_delta` signal is most informative because the gap reflects structural mispricing rather than sparse-book mechanics.
- During pregame, the spread compresses sharply, depth at BBO is thin (F33 depth-chain gap), and the `bid_consumption_velocity` and `trade_clustering_in_minute` features are most elevated — consistent with sharp-money arrival causing rapid consumption of resting liquidity.

This three-phase structure is documented in sports betting markets by the practitioner literature (Pinnacle market timing mechanics described in the Betsmart framework, 2025, https://www.youtube.com/watch?v=9OWnZI7XIec), which describes formation phase as low-limit, high-spread, sharp-attack-dominated, and later phases as high-limit, narrowing-spread, efficiency-consolidating.

---

## 3. Cross-Book Consensus as a Predictive Signal for Short-Horizon Price Convergence

### 3a. Pinnacle as the sharp-money anchor

The empirical status of Pinnacle as the price-leadership anchor in sports betting is well-established. Paul and Weinbach (2010, "The Uncertainty of Outcome and Scoring Effects on Nielsen Ratings for Monday Night Football," *Journal of Sports Economics*) and subsequent work consistently find that Pinnacle's closing line represents the sharpest available pre-game estimate of true win probability, and that lines from recreational books lag Pinnacle. Levitt (2004) establishes that Pinnacle operates more like a pure information market than a balanced-book operation — accepting sharp money and adjusting prices accordingly — while recreational books balance their books and shade toward public sentiment.

The operational consequence for the operator: `consensus_fv` computed from Pinnacle (tier-1) plus 30-46 regulated EU/AU sportsbooks is the best available external estimate of true probability. The gap `fv_delta = kalshi_fill_price − consensus_fv` is a clean measure of Kalshi's relative mis-pricing vs. the sharpest external consensus. When `fv_delta` is significantly negative (DISCOUNT regime, ≤−8¢), Kalshi's current ask is below consensus FV — a maker bid placed at or below the Kalshi ask is purchasing at a structural discount to the external market's best estimate.

**Inference vs. evidence on convergence timing.** The literature does not directly study Kalshi-vs-Pinnacle convergence at minute resolution. What is documented (inferential bridge from cross-venue lead-lag literature): in equity markets, ETF prices converge to NAV within minutes of divergence (Petajisto 2017, "Inefficiencies in the Pricing of Exchange-Traded Funds," *Financial Analysts Journal*), and S&P futures prices lead the cash index by roughly 5 minutes (Hasbrouck 1995, "One Security, Many Markets: Determining the Contributions to Price Discovery," *Journal of Finance*). In sports betting, the Pinnacle-to-recreational-book lag is documented as minutes to hours depending on market liquidity and bettor monitoring intensity. For Kalshi specifically — a regulated U.S. exchange with a growing but still limited pool of participants — the Pinnacle-to-Kalshi convergence lag is likely longer than equity ETF-NAV convergence and shorter than overnight lines in recreational books, but the precise order is an open empirical question for the corpus.

### 3b. Prediction-market arbitrage literature (Polymarket, Kalshi, PredictIt)

The Reddit practitioner community and emerging practitioner literature (AInvest 2025, "Arbitrage Opportunities in Prediction Markets: How Smart Money Profits from Price Inefficiencies," https://www.ainvest.com/news/arbitrage-opportunities-prediction-markets-smart-money-profits-price-inefficiencies-polymarket-2512/) report cross-venue price discrepancies of 2-8% between Kalshi and Polymarket for equivalent contracts. A separate project (Reddit/SideProject, May 2026, https://www.reddit.com/r/SideProject/comments/1t6zh7p/prediction_market_arbitrage_bot_for_kalshi/) reports building a real-time arbitrage bot across Kalshi/Polymarket/SX.bet that exploits these gaps. These practitioner observations confirm that Kalshi does not price-lead the broader prediction market ecosystem, and that cross-venue FV gaps are real and accessible to algorithmic participants.

The academic work on cross-venue lead-lag in correlated markets is anchored in Hasbrouck's (1995) price discovery contribution framework, which measures each venue's fractional contribution to the efficient price based on vector error correction models. In prediction market terms: if Pinnacle contributes ~80-90% of price discovery (consistent with its role as the sharp-money acceptor), then Kalshi contributes the remainder. The fv_delta signal captures the persistent component of Kalshi's lag — i.e., the portion that hasn't already been arbitraged away by faster participants.

**Cross-book consensus as a convergence-direction signal.** The core logic is: if `consensus_fv` = 45¢ and Kalshi current bid = 38¢, the maker-bid at 38¢ acquires a unit that is expected to converge toward 45¢ as information diffuses and the pregame phase consolidates. The confidence interval on this convergence is related to (a) how frequently Kalshi in fact converges to consensus before match start (corpus-measurable from per_minute_features.parquet), (b) whether the convergence is fast enough to allow maker fills before the window closes, and (c) whether the atlas cell's historical ROI was systematically associated with large vs. small `fv_delta` values. None of these CIs can be stated from the external literature — they require corpus analysis.

What the literature does confirm (Snowberg and Wolfers 2010 via Wolfers and Zitzewitz 2006, "Prediction Markets in Theory and Practice," SSRN:891232, https://www.ssrn.com/abstract=891232): prediction market prices are generally good probability estimators but not perfect, with well-documented biases (favourite-longshot bias, correlated errors in low-liquidity markets). The persistent biases mean that `consensus_fv` itself carries estimation error — it is not the ground-truth probability, only the best available external signal.

---

## 4. Market-Making vs. Alpha Capture via Maker Placement

### 4a. The taxonomy in HFT literature

The distinction between market-making and directional passive execution is increasingly well-drawn in the HFT literature, though terminology varies. The foundational taxonomy comes from practitioner classification:

| Posture | Primary revenue source | Direction thesis | Adverse selection risk | Inventory risk |
|---|---|---|---|---|
| Pure market-making | Bid-ask spread collected on both sides | Indifferent (delta-neutral) | High — filled because informed counterparty moved | Primary operational risk |
| Latency arbitrage | Cross-venue price discrepancy | No thesis, mechanical | Moderate — filled before stale quote updated | Minimal (immediate close) |
| Alpha-capture via maker | Directional thesis expressed passively | Directional (thesis: price will move to target) | Moderate — fill may coincide with adverse info | Secondary to fill-probability risk |
| Patient liquidity-taking | Directional thesis expressed via limit orders | Same as alpha-capture | Same adverse-selection structure | Minimal if thesis is right |

Brogaard, Hendershott, and Riordan (2014, "High-Frequency Trading and Price Discovery," *Review of Financial Studies*, https://doi.org/10.1093/rfs/rhu032) establish that HFT firms are not monolithic — they include pure market-makers, latency arbitrageurs, and directional traders who use maker placement. The directional HFT group's fills are associated with subsequent price moves in their direction, suggesting that their placement itself has informational content. For the operator, this is an important framing: maker bids placed at atlas-cell-informed levels are not noise; they aggregate information (the atlas edge) and this information content should result in fills being associated with price improvement.

**Kirilenko, Kyle, Samadi, and Tuzun (2017)** on HFT taxonomy in the Flash Crash context ("The Flash Crash: High Frequency Trading in an Electronic Market," *Journal of Finance*) distinguish between intermediaries (market-makers), opportunistic traders (who selectively provide liquidity when profitable), and fundamental traders. The operator's posture — making bids selectively in atlas-cell-validated situations — maps most closely to opportunistic trader: not providing liquidity continuously, not delta-neutral, but placing passive orders when the expected value (from the atlas) is positive. The risk is one-sided: unlike a market-maker who must quote both sides, the opportunistic maker can decline to bid when the signal is weak (G18 BBO honest at minute close, B25 simulator undercount).

### 4b. Fodra-Labadie directional market making

Fodra and Labadie (2012, "High-frequency market-making with inventory constraints and directional bets," arXiv:1206.4810, https://arxiv.org/abs/1206.4810) directly formalize the hybrid posture: a market-maker who also makes directional bets by posting asymmetric quotes favoring fills on the side they believe will profit. Their key result: an inventory-risk-aversion parameter allows the market-maker to tune between pure spread-collection and directional expression, trading off 15% expected PnL improvement against much higher inventory variance, or 5% PnL reduction for significantly better Sharpe ratio. This framework is instructive even though the operator's posture is even more one-sided (no two-sided quoting) — it shows that within the space of maker strategies, there exists a continuum from pure spread-collection to pure directional alpha-capture, and that the relevant risk-reward tradeoff is between expected PnL and inventory/drawdown.

For the operator: the atlas provides the directional signal (which cells have positive expected bounce); the FV anchor provides the per-leg signal (is this specific bid at a discount or premium to consensus); the paired_arb_gap features provide the joint-leg signal (is the pair's sum distorted, signaling a structural opportunity). The maker bid placement that combines all three is closer to Fodra-Labadie's directional market-making than to Ho-Stoll (1981) classical inventory-management market-making.

### 4c. "Patient liquidity-taking" framing in microstructure

Cartea, Jaimungal, and Penalva (2015, *Algorithmic and High-Frequency Trading*, Cambridge University Press, ISBN 9781107091146) introduce the framing of "patient liquidity-takers" — traders who, rather than crossing the spread immediately, post limit orders near the BBO and wait for fills, effectively "making" a trade that they could have "taken" by crossing. Their analysis shows that in markets with small tick sizes and moderate order flow, patient liquidity-taking captures the spread improvement (effective entry at bid rather than ask) at the cost of fill uncertainty and timing risk.

This is precisely the operator's entry-side mechanics for the premarket window. The key parameters in the Cartea et al. model are: (a) fill intensity as a function of queue position and spread width; (b) the opportunity cost of waiting (foregone entry if the market moves adversely before fill); (c) the benefit of fill at bid vs. ask. In Kalshi tennis terms, the last parameter is the ~1-2¢ spread improvement that separates a maker entry from a T-20m taker print — the "entry-side improvement" cited in the three-axis caveat Axis 2 of G22 as ~+10-30% improvement on the atlas headline.

**Adverse-selection-aware quoting in the one-sided maker context.** Zhao and Linetsky (2021, "High frequency automated market making algorithms with adverse selection risk control via reinforcement learning," ACM, https://dl.acm.org/doi/10.1145/3490354.3494398) propose Book Exhaustion Rate (BER) as a direct measure of adverse-selection risk — detecting when order flow is depleting the book on one side faster than normal, signaling that an informed participant is present. The analog in the operator's corpus is `bid_consumption_velocity` and `ask_consumption_velocity`: rapid consumption of the best bid (bid_consumption_velocity spike) signals aggressive selling by an informed party, which would adversely fill the maker's resting bid precisely when the direction is unfavorable. This is the adverse-selection condition that Round 3 addresses in depth.

### 4d. Summary table: literature map to operator posture

| Literature | Most relevant insight | Operator mapping |
|---|---|---|
| Glosten-Milgrom (1985) | Informed vs. uninformed trader decomposition of spread | Kalshi makers face informed fills when Pinnacle has already moved |
| Avellaneda-Stoikov (2008) | Inventory-aware spread quoting under Brownian price | Provides the quoting framework; operator adapts to one-sided, event-resolving context |
| Fodra-Labadie (2012) | Directional bets in market-making via asymmetric quotes | Best theoretical analog to alpha-capture via maker — asymmetric toward buy only |
| Cartea-Jaimungal-Penalva (2015) | Patient liquidity-takers | Most direct analog to premarket maker-bid entry |
| Brogaard-Hendershott-Riordan (2014) | HFT taxonomy: directional HFTs have informed fills | Atlas-anchored maker bids are directional, not noise |
| Brahma-Das-Magdon-Ismail (2010) | Pred market maker adaptability vs. convergence tradeoff | Bid cancellation and replacement policy (C37) |
| Fodra-Labadie (2012) | Directional bets in market-making | Asymmetric maker on one side of event pair |
| Rana et al. (2026) ParlayMarket | Coherent AMM for parlay contracts | Paired-leg sum-constraint pricing distortion dynamics |
| Groeger (2016) | LOB imbalance in prediction markets | bid/ask consumption velocity as fill-probability predictors |

### 4e. What is not in scope: market-making compensation logic

Classical market-making compensation literature (Ho-Stoll 1981; Glosten-Milgrom 1985; O'Hara 1995 *Market Microstructure Theory*) assumes the market-maker is compensated for two-sided liquidity provision and inventory risk. This logic does not apply to the operator's posture because: (a) there is no two-sided quoting, (b) inventory is one-directional (buy and hold to atlas-cell target or settlement), (c) the compensation model is atlas-derived expected bounce, not spread capture. As stated in SIMONS_MODE: "The price is not trying to be fair value. Mispricing is the default state." The operator's alpha is the atlas-calibrated mispricing, not the market-making spread.

This means the operator is exposed to adverse selection as an information-asymmetric loss, not as inventory imbalance. If filled by an informed taker (a player with new injury information, a sharp bettor who saw Pinnacle move 30 seconds earlier), the fill occurs at a price that is already stale relative to the information set. The remediation is the FV anchor filter (discard bids where `fv_delta` is already PREMIUM) and the partner-leg monitoring (if partner leg's bid moves abruptly, information has hit the pair and the own-leg bid should be cancelled before fill).

---

## Synthesis and Cross-Reference

The four sub-questions converge on a coherent picture for the premarket execution policy:

1. **Paired structure** creates coupled fill-and-adverse-selection risks not modeled in standard single-asset market-making. The options-parity and ParlayMarket literatures provide the analytical frame; empirical quantification requires corpus analysis of paired_arb_gap dynamics across premarket phases (E12).

2. **Premarket phases** are empirically real (documented in Betfair EPL and soccer literatures), show a predictable pattern of spread compression and depth increase toward match start, and the timing structure supports the three-phase (formation/stable/pregame) decomposition underlying the B14/G17 premarket vs. in-match decomposition.

3. **Cross-book consensus** (fv_delta) is the most theoretically well-grounded predictive signal available: Pinnacle's price-leadership role is empirically established, and the Kalshi-vs-Pinnacle gap is structurally analogous to ETF-NAV basis or Betfair-vs-recreational-book spread. The direction of the gap (DISCOUNT/FAIR/PREMIUM) is a convergence-direction signal; the magnitude is a confidence-in-convergence signal.

4. **Alpha-capture via maker** is the correct framing (not market-making): the strategy is directional (atlas-validated cells), passive (maker bids not taker orders), and compensated by price-path convergence to atlas target, not by spread collection. Adverse selection is a downside risk (filled by informed counterparty), not an operational cost of market-making. The relevant literature is Fodra-Labadie directional quoting, Cartea et al. patient liquidity-taking, and Brogaard et al. HFT directional taxonomy.

All four axes connect to G22's three-axis deployment math: the premarket window is the vehicle for implementing Axis 2 (entry-side improvement, ~+10-30% multiplier) and the paired structure means Axis 2 improvement on one leg must be evaluated jointly with the partner leg's state (E12 premarket phases, B16 Layer A/B/C separation).

---

*References (full citations)*

- Avellaneda, M. and Stoikov, S. (2008). "High-frequency trading in a limit-order book." *Quantitative Finance*, 8(3), 217–224. DOI: 10.1080/14697680701381228.
- Avery, C. and Chevalier, J. (1999). "Identifying Investor Sentiment from Price Paths: The Case of Football Betting." *Journal of Business*, 72(4), 493–521. DOI: 10.1086/209625.
- Bergault, P., Evangelista, D., Guéant, O., and Vieira, D. (2022). "Closed-form approximations in multi-asset market making." arXiv:1810.04383. https://arxiv.org/abs/1810.04383
- Brahma, A., Das, S., and Magdon-Ismail, M. (2010). "Comparing Prediction Market Structures, With an Application to Market Making." arXiv:1009.1446. https://arxiv.org/abs/1009.1446
- Brogaard, J., Hendershott, T., and Riordan, R. (2014). "High-Frequency Trading and Price Discovery." *Review of Financial Studies*, 27(8), 2267–2306. https://doi.org/10.1093/rfs/rhu032
- Cartea, Á., Jaimungal, S., and Penalva, J. (2015). *Algorithmic and High-Frequency Trading*. Cambridge University Press. ISBN: 9781107091146.
- Fodra, P. and Labadie, M. (2012). "High-frequency market-making with inventory constraints and directional bets." arXiv:1206.4810. https://arxiv.org/abs/1206.4810
- Garleanu, N. and Pedersen, L. (2011). "Margin-Based Asset Pricing and Deviations from the Law of One Price." *Review of Financial Studies*, 24(6), 1980–2022. https://doi.org/10.1093/rfs/hhr027
- Glosten, L. and Milgrom, P. (1985). "Bid, ask and transaction prices in a specialist market with heterogeneously informed traders." *Journal of Financial Economics*, 14(1), 71–100. https://doi.org/10.1016/0304-405X(85)90044-3
- Groeger, J. (2016). "The Informational Content of the Limit Order Book: An Empirical Study of Prediction Markets." arXiv:1609.03471. https://arxiv.org/abs/1609.03471
- Hasbrouck, J. (1995). "One Security, Many Markets: Determining the Contributions to Price Discovery." *Journal of Finance*, 50(4), 1175–1199.
- Ho, T. and Stoll, H. (1981). "Optimal Dealer Pricing Under Transactions and Return Uncertainty." *Journal of Financial Economics*, 9(1), 47–73.
- Kirilenko, A., Kyle, A.S., Samadi, M., and Tuzun, T. (2017). "The Flash Crash: High Frequency Trading in an Electronic Market." *Journal of Finance*, 72(3), 967–998.
- Levitt, S. (2004). "Why Are Gambling Markets Organised Differently from Financial Markets?" *Economic Journal*, 114(495), 223–246.
- Nechepurenko, M. (2026). "Resolution-Aware Perpetual Futures on Binary Prediction Markets." Semantic Scholar. https://www.semanticscholar.org/paper/18375b082ac7ea58e1ab560dec571beaeb45e9b1
- Rana, R., Nadkarni, V., Moshrefi, N., and Viswanath, P. (2026). "ParlayMarket: Automated Market Making for Parlay-style Joint Contracts." Semantic Scholar. https://www.semanticscholar.org/paper/722bda1229b32ab3f322c31aa1be05d3a527cefc
- Reade, J. et al. (2020). "Informational efficiency and behaviour within in-play prediction markets." University of Reading Economics Discussion Paper. https://www.reading.ac.uk/web/files/economics/emdp201920.pdf
- Singleton, C., Reade, J., and Ramirez, P. (2022). "Betting on a buzz: Mispricing and inefficiency in online sportsbooks." *International Journal of Forecasting*. https://doi.org/10.1016/j.ijforecast.2022.07.011
- Snowberg, E., Wolfers, J., and Zitzewitz, E. (2012). "Prediction Markets for Economic Forecasting." NBER Working Paper. https://ssrn.com/abstract=2102420
- Tondapu, N. (2024). "Efficient Market Dynamics: Unraveling Informational Efficiency in UK Horse Racing Betting Markets Through Betfair's Time Series Analysis." arXiv:2402.02623. https://arxiv.org/abs/2402.02623
- Wolfers, J. and Zitzewitz, E. (2006). "Prediction Markets in Theory and Practice." SSRN:891232. https://ssrn.com/abstract=891232
- Zhao, M. and Linetsky, V. (2021). "High frequency automated market making algorithms with adverse selection risk control via reinforcement learning." ACM ICAIF. https://dl.acm.org/doi/10.1145/3490354.3494398
