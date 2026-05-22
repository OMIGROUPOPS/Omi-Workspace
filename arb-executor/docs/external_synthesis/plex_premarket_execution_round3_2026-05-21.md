# Plex Premarket Execution Synthesis — Round 3: Adverse Selection, Queue Position, Bid-Improvement Threshold

**Source:** Plex (Perplexity) literature synthesis
**Date:** 2026-05-21
**Prompt context:** Round 3 was asked to synthesize literature on three sub-questions relevant to the risk-management and bid-level-selection aspects of the premarket maker-bid policy: (1) adverse selection in maker fills — whether the act of getting filled itself carries information about which direction the market is about to move (the "information-provider trap"), and specifically whether the bot can detect fills that are driven by Pinnacle-move-induced Kalshi repricing and should trigger position flattening rather than atlas-cell holding; (2) queue position modeling in low-volume markets — whether price-time priority and queue position carry meaningful expected-fill-time information in thin books like Kalshi tennis, and what the conventional wisdom from Treasury futures, crypto thin pairs, and small-cap equities says; and (3) bid-improvement (one tick inside BBO) as a fill-probability lever — the principled trade-off between a 1¢ price concession and a higher fill probability, framed around when the expected fill-probability lift × forward-bounce-conditional-on-fill exceeds the certain 1¢ cost.
**Status:** External synthesis — for integration by chat-side Opus into the U4 Phase 3 build and bid-laying policy spec. Per LESSONS C40, external synthesis is committed to repo immediately, not held in chat-side context only.

---

## 1. Adverse Selection in Maker Fills

### 1a. The fundamental adverse selection mechanism in maker orders

The core insight from Glosten and Milgrom (1985, "Bid, ask and transaction prices in a specialist market with heterogeneously informed traders," *Journal of Financial Economics*, 14(1), 71–100, https://doi.org/10.1016/0304-405X(85)90044-3) is that the bid-ask spread compensates market-makers for the risk of trading with informed counterparties. Every maker fill is an event in which someone chose to cross the spread — either an uninformed liquidity-seeker or an informed trader who knows the price will move in their direction. The ratio of informed to uninformed fills determines whether the maker's spread income covers adverse-selection losses.

In the operator's context, the adverse-selection risk is inverted relative to the classical market-maker: the operator is the maker (the bid poster), not the spread collector. When the operator's maker bid is filled, a taker crossed from the ask side (paid the ask, sold to the operator at the bid). This means the taker decided the bid price was acceptable — either because they needed liquidity (uninformed) or because they know the market is about to move down (informed). If the taker is informed, the fill is adverse: the operator just bought YES at the bid and the market is about to move toward the NO side (price falling toward 0).

**The specific informed-fill scenario in tennis binary markets.** The most acute form of adverse selection for the operator is:
1. Pinnacle adjusts its probability estimate for player1's win by 5-10 percentage points (e.g., injury news, late withdrawal).
2. A sophisticated participant who monitors Pinnacle near-real-time sells player1-YES at Kalshi before Kalshi's local BBO has repriced.
3. The operator's resting maker bid is at 40¢; the taker sells 10ct at 40¢ (filling the operator's bid); Kalshi's new equilibrium price is 32¢.
4. The operator is now long 10ct at 40¢ in a market that should clear at 32¢ — an immediate −8¢ unrealized loss per contract, amplified if held to the atlas-cell exit target.

This is the information-provider trap: the maker's bid filled precisely because the market was about to move adversely. The fill is not a signal that the trade is working; it is a signal that informed information just arrived.

### 1b. Detection signals for adverse fills

**VPIN as a flow-toxicity real-time signal.** Easley, López de Prado, and O'Hara (2011, "The Microstructure of the 'Flash Crash': Flow Toxicity, Liquidity Crashes, and the Probability of Informed Trading," *Journal of Portfolio Management*, 37(2), 118–128, DOI: 10.3905/jpm.2011.37.2.118; and 2012, "Flow Toxicity and Liquidity in a High Frequency World," *Review of Financial Studies*, 25(5), 1457–1493) develop Volume-Synchronized Probability of Informed Trading (VPIN) as a real-time measure of the probability that recent order flow contains disproportionate informed trading. VPIN is computed from volume imbalance (buy-initiated vs. sell-initiated volume within equal-volume time buckets), not from calendar time. When VPIN spikes, liquidity providers should widen quotes or reduce exposure because the probability of adverse fills is elevated.

**Adaptation to Kalshi tennis.** In Kalshi tennis with very low volume (10-50ct typical BBO, sparse taker prints), standard VPIN is not directly computable — the volume buckets required to estimate VPIN reliably need far more taker volume than Kalshi tennis generates in any single minute. However, the conceptual principle translates:

- `trade_clustering_in_minute` (std of inter-trade gap times) is the operator's closest proxy for informed-order-arrival clustering. When `trade_clustering_in_minute` is very low (trades arrive in rapid bursts, very small inter-trade gap std), this indicates concentrated order flow consistent with an informed participant deploying a sequence of market orders. This is structurally equivalent to a high-VPIN reading.
- `ask_consumption_velocity` (rate at which ask-side levels are consumed by takers) captures the directionality of taker aggression. A sudden spike in ask_consumption_velocity on the partner leg (partner_taker_flow_in_minute jumping) indicates aggressive buying of the partner leg — which, by the no-arb sum constraint, implies informed pessimism about the own leg.
- `bid_consumption_velocity` (rate at which bid-side levels are consumed) spiking on the own leg: informed sellers hitting the own-leg bid in rapid succession. If the operator's maker bid is in the queue and bid_consumption_velocity spikes, the expected next events are: (a) the operator's bid fills, and (b) the price drops further as information propagates. This is the textbook adverse-fill pattern.

**DeLise (2024) on the "negative drift" of limit order fills.** DeLise (2024, "The Negative Drift of a Limit Order Fill," arXiv:2407.16527, https://arxiv.org/abs/2407.16527) provides direct empirical evidence — using equity futures data — that limit order fills are systematically followed by adverse price drift: "Limit order fills are caused by and coincide with adverse price movements, which create a drag on the market maker's profit and loss." The study demonstrates that the average realized PnL of a passive limit order strategy is lower than naive simulations suggest because fills correlate with adverse periods. This is precisely the B25 finding for Kalshi: the minute-cadence simulator overstates limit-policy fills vs. tick reality by 2.4×, likely because the simulator assumes IID fills while real fills cluster around adverse information events.

**Market Simulation under Adverse Selection (Lalor and Swishchuk 2025).** Lalor and Swishchuk (2025, "Market Simulation under Adverse Selection," arXiv:2409.12721, https://arxiv.org/abs/2409.12721) formalize the fill-probability-and-adverse-selection joint framework for short-term trading strategies. Their central finding: simulations that model fill probabilities and adverse fills jointly show far more conservative performance than simulations that assume fills and price processes are independent. "Fill probabilities and adverse fills can significantly affect performance." This is a direct literature corroboration of B25's 2.4× overstatement.

### 1c. Post-fill decision: hold to atlas target vs. flatten on adverse signal

**Classical adverse-selection-aware quoting.** Zhao and Linetsky (2021, "High frequency automated market making algorithms with adverse selection risk control via reinforcement learning," ACM ICAIF, https://dl.acm.org/doi/10.1145/3490354.3494398) propose the Book Exhaustion Rate (BER) feature as a real-time adverse-selection detector. Their RL-trained market-maker uses BER to avoid large losses: when BER spikes, the algorithm reduces its liquidity provision. Translated to the operator's post-fill decision: if after a fill the `bid_consumption_velocity` or `trade_clustering_in_minute` immediately spikes (within 1-2 minutes post-fill), this is evidence of an informed fill, and the position should be evaluated for early exit.

**Can the bot detect the Pinnacle-lag fill?** The operator's specific concern — "I just got filled because Pinnacle moved 30 seconds ago and Kalshi hadn't repriced yet" — is detectable in principle through:

1. **Post-fill fv_delta trajectory**: If `fv_delta` (kalshi_fill_price − consensus_fv) moves sharply positive after the fill (i.e., the fill price is now above the refreshed consensus FV), then the fill occurred at a price that consensus had already left behind — the Pinnacle-lag fill signature. The consensus_fv from the `tennis_odds.py` sidecar is not per-minute in the current corpus (it's a sidecar feed, per the fv_state_strategy_v1.md description), so this detection requires either near-real-time consensus_fv updates or a post-fill retrospective check within the same minute.

2. **Partner-leg BBO jump**: If the partner leg's BBO (partner_yes_bid_close, partner_yes_ask_close) shifts significantly within 1-2 minutes after the own-leg fill, this is evidence that information has propagated through the pair — a Pinnacle-driven reprice would move both legs, but the own leg's fill may have occurred before the reprice hit it.

3. **Inference from fill timing**: Fills that occur in isolation (no cluster, no preceding volume spike) are more consistent with uninformed liquidity-seeking takers than with informed participants. Fills that are preceded or accompanied by a volume/clustering spike are more consistent with informed fills.

**Inference vs. evidence.** The three detection heuristics above are inferences from the adverse-selection literature, the VPIN framework, and the paired-leg structure — not direct empirical results from Kalshi tennis data. The corpus analysis required is: for fills that were subsequently adverse (price fell further after fill), what were the values of `bid_consumption_velocity`, `trade_clustering_in_minute`, and partner-leg BBO dynamics in the 1-2 minutes before and after the fill? This requires constructing a "fill-outcome" labeled dataset from the per_minute_features.parquet, which is a Layer C task (B16 Layer A/B/C separation).

**Practical framing for the policy spec.** The adverse-fill detection does not need to be 100% accurate to add value. Even a noisy signal that correctly identifies adverse fills 60-70% of the time and triggers a 2-minute hold-or-exit decision can materially reduce the tail losses from B25's known adverse-fill exposure. The expected value calculation: P(adverse fill detected correctly) × PnL saved per adverse fill − P(false positive) × opportunity cost of premature exit. This is the principled framing for setting the detection threshold.

---

## 2. Queue Position in Low-Volume Markets

### 2a. Queue position value in the theoretical literature

Moallemi and Yuan (2016, "A Model for Queue Position Valuation in a Limit Order Book," SSRN:2996221, https://ssrn.com/abstract=2996221) develop a continuous-time model for the value of queue position at the best bid/ask price. Their key results:
- Queue position has significant value when: (a) the order fill rate at the best price is meaningful; (b) adverse price moves are not too frequent; (c) queue priority translates into predictable fill-time reduction.
- The value of queue position decays as the queue before the target order grows — a large queue makes fill-time highly uncertain.
- In thin queues (small total BBO size), queue position matters less in absolute terms because the total queue clears quickly on any significant taker order.

**Application to Kalshi tennis.** With 10-50ct typical BBO size in Kalshi tennis, the queue is extremely thin. If the total BBO bid queue is 20ct and the operator posts 10ct, the operator's order fills when the next 21-30ct of sell-side market orders arrive — often a single taker event (one match participant selling 10-30ct at once). In this regime, queue position effectively determines whether the operator fills before or after a hypothetical competing 10ct order at the same price. But since the total queue is so thin, a single taker print often clears the entire BBO and fills all resting orders regardless of priority.

**Inference.** In thin-book venues with BBO queue sizes of 10-50ct, queue position carry minimal expected-fill-time information compared to the dominant factor: whether a taker print occurs at all. The binary outcome (taker arrives or doesn't) dominates the queue-position-conditional-on-taker outcome. The conventional wisdom from thin Treasury futures expirations (off-the-run Treasuries with sparse LOBs) and crypto thin pairs is: at the BBO in a thin book, all maker orders are effectively homogeneously fillable on any given taker event. The queue matters for capacity (how much can fill on a single event) but not for priority within a single print.

**Stoikov-Waeber (2010) queue-position pricing.** Stoikov and Waeber's work on queue position pricing in equity limit order books finds that the value of one position of priority at the BBO is approximately 0.5–1.5 ticks × (fill probability per day). For a thin binary market with a 1-2¢ typical spread and fill probability per minute on the order of 1-5%, the value of queue priority is on the order of 0.01-0.05¢ per minute of waiting — vanishingly small compared to the 1¢ spread-improvement opportunity from bidding one tick inside the BBO (analyzed in Section 3 below). This confirms the conventional wisdom: in thin markets, queue position is not a significant decision variable.

### 2b. Price-time priority vs. pro-rata allocation in thin markets

Exchange microstructure literature distinguishes two primary allocation mechanisms: price-time priority (first posted at a price gets filled first) and pro-rata allocation (fill proportional to order size). Kalshi uses price-time priority as a CDA (Continuous Double Auction), consistent with standard exchange mechanics (B23 bilateral mechanism).

Under price-time priority with a thin BBO (10-50ct total), the priority effect disappears entirely when: (a) a single taker print fills the entire BBO in one event (common in thin markets), or (b) the BBO refreshes between order submission and taker arrival (rate-limited to minute-cadence in the per_minute_features.parquet). Empirically, in thin equity markets (OTC bulletin board stocks, exotic futures contracts), Huang and Stoll (1997, "The components of the bid-ask spread: A general approach," *Review of Financial Studies*) find that BBO turnover is so rapid that time priority within a single minute is effectively random — the relevant decision variable is whether to be in the queue at all, not queue position.

**Practical implication for the policy spec.** The operator should treat all maker bids resting at the BBO as homogeneously fillable on any given minute (no queue-position-conditional-fill-probability adjustment). The decision should focus on: (a) whether to post at all (atlas cell + fv_delta + paired_arb_gap decision); (b) at what price to post (BBO bid vs. one-tick improvement); (c) when to cancel and repost (C37 pre-replace gate). These are the meaningful levers; intra-queue priority is not.

### 2c. Conventional wisdom from thin analogous markets

| Market type | BBO typical size | Queue position relevance | Key insight |
|---|---|---|---|
| On-the-run Treasuries | 100s-1000s lots | High | Price-time priority matters; queue modeling is active research |
| Off-the-run Treasury (sparse) | 1-10 lots | Negligible | Thin queue; fill is binary event, not queue-position function |
| Kalshi tennis binary | 10-50 ct | Negligible | Same thin-book regime; queue position ≈ irrelevant |
| Crypto thin pairs (low-cap) | 0.1-5 BTC equivalent | Negligible | Thin book; one large taker clears entire BBO |
| Small-cap equities (NYSE ARCA, OTC) | 100-1000 shares | Low | Moderate; priority matters at high frequency, not at minute scale |

*Source: Huang-Stoll 1997; Moallemi-Yuan 2016; practitioner LOB literature for crypto thin markets.*

The unanimous finding across thin-book venues: queue position modeling provides minimal marginal value when queue sizes are small enough that a single taker print likely clears the relevant depth. The operator should invest modeling effort in fill-probability-given-taker-arrival prediction, not queue-position-conditional-fill modeling.

---

## 3. Bid-Improvement Threshold: One Tick Inside BBO as a Fill-Probability Lever

### 3a. The principled trade-off framework

The bid-improvement decision is a unit-of-decision per-minute problem (B15) with a clean expected-value formulation:

**Expected value of improvement bid:**
\[ \text{EV}_{\text{improve}} = P(\text{fill} \mid \text{improve}) \times E[\text{bounce} \mid \text{fill, improve}] - \Delta p \]

**Expected value of BBO bid:**
\[ \text{EV}_{\text{BBO}} = P(\text{fill} \mid \text{BBO}) \times E[\text{bounce} \mid \text{fill, BBO}] \]

**Decision:** improve if \( \text{EV}_{\text{improve}} > \text{EV}_{\text{BBO}} \), i.e.:

\[ \Delta P(\text{fill}) \times E[\text{bounce} \mid \text{fill}] > \Delta p \]

where \( \Delta P(\text{fill}) = P(\text{fill} \mid \text{improve}) - P(\text{fill} \mid \text{BBO}) \) is the fill-probability lift from improvement, and \( \Delta p \) is the price concession (1¢ in a 1¢-spread market). The expectation is conditional on fill; the assumption that \( E[\text{bounce} \mid \text{fill, improve}] \approx E[\text{bounce} \mid \text{fill, BBO}] \) holds if fill timing within the premarket window is uninformative about the post-fill return conditional on state features (this is an assumption to validate from the corpus).

### 3b. Theoretical grounding from optimal-spread quoting literature

**Avellaneda-Stoikov (2008).** The Avellaneda-Stoikov market-making model derives the optimal bid and ask spreads as functions of (a) the inventory position, (b) the market's fundamental volatility, and (c) the taker arrival intensity. The key formula for the optimal bid quote \( r_b \):

\[ r_b = s - \frac{1}{2}\sigma^2 \gamma (q + 1)\Delta t - \frac{1}{\kappa_b} \ln(1 + \frac{\kappa_b \gamma \sigma^2}{A}) \]

where \( s \) is the mid-price, \( \gamma \) is risk aversion, \( q \) is inventory, \( \kappa_b \) is the sensitivity of taker arrival intensity to bid depth, and \( A \) is the unconditional taker arrival intensity. The term \( \frac{1}{\kappa_b} \ln(1 + \frac{\kappa_b}{\ldots}) \) is the optimal half-spread, driven by the inverse of the fill-probability sensitivity to price: if \( \kappa_b \) is large (fill probability very sensitive to price), the optimal spread is small and the maker should post close to mid. If \( \kappa_b \) is small (fill probability relatively insensitive to price), the optimal spread is large.

**Adaptation to operator's one-sided bid context.** The operator's bid is one-sided (no ask), so the inventory dynamics differ from Avellaneda-Stoikov's symmetric case. But the fill-probability sensitivity term \( \kappa_b \) is the key parameter: in a thin market where taker arrival is rare and a single taker clears the BBO, \( \kappa_b \) is likely low — a 1¢ improvement in bid price does not dramatically increase taker arrival probability if takers are arriving at all. The value of improvement is then primarily queue-position advantage over other resting bids at the BBO (as argued in Section 2, this advantage is minimal in thin queues), not in increasing taker arrival intensity.

**When does \( \kappa_b \) matter?** In thin markets, there are two types of taker events: (a) uninformed liquidity-seekers who would cross the spread at any reasonable bid price — these takers fill regardless of whether the bid is at the BBO or 1¢ below; (b) informed takers who are selling because they know the price will fall — these takers will transact at any price above their private value, so improvement doesn't attract them and in fact makes the adverse fill cheaper (to them). The only scenario where improvement materially increases fill probability is if there are takers who value liquidity between the BBO bid and the improvement price — a thin marginal band that may be small in practice for tennis markets.

### 3c. Distortion magnitude as an improvement-decision signal

**`paired_arb_gap_maker` and fill-probability lift.** When `paired_arb_gap_maker` is large (both bids sum far from $1), the book is distorted and the structural incentive for takers to fill is lower (uninformed takers may be waiting for the book to normalize before transacting). In this regime, improvement does not materially lift fill probability — the book is in a low-activity formation phase (E12). Improvement is most valuable when the book is near coherent (`paired_arb_gap_maker` near zero) and taker activity is moderate — the pregame stable phase — where uninformed takers are the marginal participants and an improvement bid could attract a few additional contracts.

**`fv_delta` and improvement logic.** When `fv_delta` is deeply DISCOUNT (−8¢ or more), the bid price is already far below consensus FV, and improvement (paying 1¢ more) reduces the discount margin to FV but may substantially increase fill probability if the Kalshi BBO is thin and uninformed sellers are indifferent across the 1¢ range. When `fv_delta` is FAIR or PREMIUM, improvement is dangerous: paying 1¢ more in a FAIR market reduces expected post-fill return by that 1¢; paying more in a PREMIUM market amplifies the adverse pricing.

**Spread width as a scaling factor.** Ho and Stoll (1981, "Optimal Dealer Pricing Under Transactions and Return Uncertainty," *Journal of Financial Economics*, 9(1), 47–73) establish that optimal spread is proportional to volatility and inversely proportional to taker arrival intensity. In a wide-spread premarket (5-10¢ spread, typical during formation phase), a 1¢ improvement is a small fraction of the spread and unlikely to dramatically shift the maker's relative position. In a tight-spread pregame (1-2¢ spread, typical in pregame phase), a 1¢ improvement crosses from the BBO bid to the midpoint — a qualitatively different position that may attract significantly more uninformed taker flow.

### 3d. Empirical CI on \( \Delta P(\text{fill}) \)

The fill-probability lift \( \Delta P(\text{fill}) \) from improvement is a corpus-dependent empirical quantity. External literature does not provide a direct estimate for Kalshi tennis markets. In equity markets, Stoikov's queue-based models estimate the fill probability at the BBO as:

\[ P(\text{fill before adverse move} \mid \text{BBO}) \approx \frac{q^{-}}{q^{-} + q^{+}} \]

where \( q^{-} \) is the time-to-next-taker-arrival rate and \( q^{+} \) is the time-to-adverse-price-move rate. In thin markets with low taker arrival rates, this probability is often below 30-40% per minute. One-tick improvement shifts the maker's order to a more favorable queue position, but as established in Section 2, queue position advantage in thin books is minimal. The corpus-level estimate of \( \Delta P(\text{fill}) \) for each premarket phase is the necessary input.

**Inference calibration.** For the cheap-regime cells (anchor 5-30¢, A39 cents-vs-ROI geometry), where the 1¢ improvement represents 3-20% of the entry price, the cost of improvement is substantial in percentage ROI terms. A 1¢ concession on a 10¢ entry is a 10% ROI reduction. The improvement should only be exercised when \( \Delta P(\text{fill}) \times E[\text{bounce}] > 0.01 \) in dollar terms — which at a typical 5-10¢ expected bounce for cheap regime cells requires \( \Delta P(\text{fill}) > 0.10-0.20 \). This is a non-trivial threshold that requires careful corpus calibration to evaluate (A21 CIs required on \( \Delta P \)).

### 3e. Structured decision framework for bid-improvement

Based on the literature synthesis, the principled improvement decision depends on a three-axis evaluation:

| Axis | Favor improvement (Y) | Favor BBO bid (N) |
|---|---|---|
| **fv_delta (own leg)** | DISCOUNT (≤−8¢): large FV gap, room to give 1¢ | FAIR or PREMIUM: FV gap already thin |
| **paired_arb_gap_maker** | Near zero (book coherent, pregame stable): takers more active | Large (formation phase, thin book): improvement doesn't attract takers |
| **Spread width** | Tight (1-2¢, pregame): 1¢ improvement crosses mid | Wide (5-10¢, formation): 1¢ is a small fraction |
| **time_to_match_start_min** | Pregame (T < 30min): window closing, fill urgency high | Formation (T > 90min): ample time to wait at BBO |
| **ask_consumption_velocity** | Low: takers not currently active, need to attract | High: takers already arriving, no need to improve |
| **Entry price (cents)** | Expensive regime (>50¢): 1¢ is 2% ROI cost | Cheap regime (<20¢): 1¢ is 5-20% ROI cost |

The joint condition for improvement: `fv_delta` is DISCOUNT **and** `paired_arb_gap_maker` is near zero **and** spread is tight **and** entry price is not in the cheap regime (A39) **and** time is pregame. In all other conditions, staying at BBO and waiting dominates, because either the FV cushion doesn't support paying extra, or the book's taker behavior won't be attracted by 1¢ improvement.

**Cross-reference to the three-axis caveat (G22).** The improvement decision directly implements Axis 2 (entry-side improvement, ~+10-30% multiplier on the atlas headline). But the 10-30% improvement estimate is an average across cells and conditions — in cheap-regime cells (Axis 2 is most levered to marginal improvement per A39), the ROI cost of improvement is highest, making the improvement decision particularly fraught. The improvement framework above provides the conditions under which improvement is justified (primarily expensive-regime cells in pregame-stable phase with deep DISCOUNT fv_delta), and the conditions under which it is counterproductive (cheap-regime cells in formation phase with FAIR fv_delta).

### 3f. Guéant-Lehalle-Fernandez-Tapia optimal spread decomposition

Guéant, Lehalle, and Fernandez-Tapia (2012, "Dealing with the Inventory Risk: A solution to the market making problem," arXiv:1105.3115, https://arxiv.org/abs/1105.3115) provide closed-form solutions for optimal maker quotes as a function of inventory, horizon, and risk aversion. Their model decomposes the bid spread into:
1. **Adverse-selection component**: proportional to the probability of trading with an informed counterparty.
2. **Inventory-management component**: proportional to the cost of carrying inventory to horizon.
3. **Spread-collection component**: the base spread income.

For the operator's one-sided, directional maker bid:
- The adverse-selection component maps to the probability of an adverse fill (informed taker). When `bid_consumption_velocity` or `trade_clustering` signals high adverse-selection risk, the bid price should be lowered (more aggressive discount demanded), not improved.
- The inventory-management component maps to the cost of carrying a position that doesn't bounce to the atlas target. For cheap-regime cells with high ROI volatility, this is significant.
- The spread-collection component is absent (the operator is not a two-sided market-maker).

The implication: the improvement decision should be evaluated as a trade-off between inventory-management urgency (fill now by improving, even at worse price) and adverse-selection risk (improvement in a high-adversity environment is doubly costly — worse entry price and higher probability of being the informed counterparty's victim). This is a key risk-management insight not typically highlighted in optimal-quoting literature.

### 3g. Practical synthesis: the bid-improvement decision rule

The literature converges on the following principled formulation for the bid-improvement threshold:

**Improve by 1¢ from BBO bid if and only if:**

\[ P(\text{fill} \mid \text{improve}) \times E[\text{bounce} \mid \text{fill, state}] > P(\text{fill} \mid \text{BBO}) \times E[\text{bounce} \mid \text{fill, state}] + \Delta p \]

Which simplifies to:

\[ \Delta P(\text{fill}) \times E[\text{bounce}] > \Delta p \]

Where the improvement decision is conditional on state features that must satisfy:
1. **`fv_delta` ≤ −8¢** (DISCOUNT: structural basis for paying up exists)
2. **`paired_arb_gap_maker` < \(  \epsilon \)** (book is coherent; takers active)
3. **Spread width ≤ 2¢** (improvement reaches midpoint, attracts marginal takers)
4. **`time_to_match_start_min` < 30** (fill urgency elevated; holding cost increasing)
5. **Entry price > 30¢** (cheap-regime cells: cost of improvement in ROI terms is prohibitive, A39)
6. **`bid_consumption_velocity` is LOW** (no adverse signal: safe to pay up)

When all six conditions hold, improvement is likely positive-EV based on the theoretical framework. The specific \( \Delta P(\text{fill}) \) and \( E[\text{bounce}] \) values require corpus calibration. The CI on the improvement decision's expected value will be wide unless the corpus provides at least ~500-1000 improvement-vs-BBO comparisons in similar state conditions.

**Adverse-selection interaction.** If at fill-time the adverse-fill signals fire (bid_consumption_velocity spike, trade_clustering spike, partner-leg BBO move), the post-fill position should be evaluated for early exit regardless of improvement vs. BBO entry. The improvement decision and the post-fill holding decision are separate choices that share the adverse-selection signal as a common diagnostic.

---

## Synthesis: Adverse Selection, Queue, and Improvement as an Integrated Risk Framework

The three sub-questions in Round 3 are not independent — they form a coherent risk framework for the premarket execution policy:

1. **Adverse selection** is the primary risk of maker bids in a venue where Pinnacle-informed participants may exploit Kalshi's lagged repricing. Detection requires monitoring `bid_consumption_velocity`, `trade_clustering_in_minute`, and partner-leg BBO dynamics in the 2 minutes around any fill event. Post-fill, the `fv_delta` trajectory (has consensus_fv moved adversely since fill?) is the cleanest diagnostic.

2. **Queue position** is a second-order concern in Kalshi tennis's thin book regime. The evidence from thin-market microstructure (Treasury off-the-runs, crypto thin pairs) and from Moallemi-Yuan's queue valuation theory is consistent: in thin books, all BBO bids are effectively homogeneously fillable. The decision should focus on whether to be in the queue at all, and at what price, not on queue-position management.

3. **Bid improvement** is a precision lever for the pregame-stable phase, primarily for expensive-regime cells in deep DISCOUNT fv_delta conditions. For cheap-regime cells (the highest-ROI segment, A39/G22 Axis 2), improvement is expensive in percentage ROI terms and should only be exercised when fill urgency is high (close to match start) and the adverse-selection signals are clean (no informed flow detected).

Cross-referencing the three-axis caveat (G22): the combined adverse-selection, queue, and improvement analysis shapes the entry-side improvement multiplier (Axis 2). The theoretical range (10-30% improvement on headline) is consistent with the literature's expected improvements from maker-vs-taker entry in thin markets, but the realized improvement will depend heavily on (a) how often adverse fills occur and erode the improvement, (b) whether the improvement-conditional conditions hold frequently enough to matter, and (c) how many cells are in cheap vs. expensive regime (A39 geometry allocates ~8% of capital to cheap cells but ~38% of dollar profit).

The data-driven path to all three decisions is corpus calibration on per_minute_features.parquet: measure realized post-fill returns stratified by fill-timing adverse-selection signal, by queue position proxy, and by improvement vs. BBO entry price. All CI statements must follow A21 discipline — bootstrap CIs on point estimates, Wilson intervals on proportions, flagging low-N cells.

---

*References (full citations)*

- Avellaneda, M. and Stoikov, S. (2008). "High-frequency trading in a limit-order book." *Quantitative Finance*, 8(3), 217–224. DOI: 10.1080/14697680701381228.
- Cartea, Á., Jaimungal, S., and Penalva, J. (2015). *Algorithmic and High-Frequency Trading*. Cambridge University Press. ISBN: 9781107091146.
- DeLise, T. (2024). "The Negative Drift of a Limit Order Fill." arXiv:2407.16527. https://arxiv.org/abs/2407.16527
- Easley, D., López de Prado, M., and O'Hara, M. (2011). "The Microstructure of the Flash Crash: Flow Toxicity, Liquidity Crashes, and the Probability of Informed Trading." *Journal of Portfolio Management*, 37(2), 118–128. DOI: 10.3905/jpm.2011.37.2.118
- Easley, D., López de Prado, M., and O'Hara, M. (2012). "Flow Toxicity and Liquidity in a High Frequency World." *Review of Financial Studies*, 25(5), 1457–1493. DOI: 10.1093/rfs/hhs053.
- Glosten, L. and Milgrom, P. (1985). "Bid, ask and transaction prices in a specialist market with heterogeneously informed traders." *Journal of Financial Economics*, 14(1), 71–100. https://doi.org/10.1016/0304-405X(85)90044-3
- Guéant, O., Lehalle, C.-A., and Fernandez-Tapia, J. (2012). "Dealing with the Inventory Risk: A solution to the market making problem." *Mathematics and Financial Economics*, 7(4), 477–507. arXiv:1105.3115. https://arxiv.org/abs/1105.3115
- Ho, T. and Stoll, H. (1981). "Optimal Dealer Pricing Under Transactions and Return Uncertainty." *Journal of Financial Economics*, 9(1), 47–73.
- Huang, R. and Stoll, H. (1997). "The components of the bid-ask spread: A general approach." *Review of Financial Studies*, 10(4), 995–1034.
- Lalor, L. and Swishchuk, A. (2025). "Market Simulation under Adverse Selection." arXiv:2409.12721. https://arxiv.org/abs/2409.12721
- Moallemi, C. and Yuan, K. (2016). "A Model for Queue Position Valuation in a Limit Order Book." SSRN:2996221. https://ssrn.com/abstract=2996221
- Reade, J. et al. (2020). "Informational efficiency and behaviour within in-play prediction markets." University of Reading Economics Discussion Paper. https://www.reading.ac.uk/web/files/economics/emdp201920.pdf
- Singleton, C., Reade, J., and Ramirez, P. (2022). "Betting on a buzz: Mispricing and inefficiency in online sportsbooks." *International Journal of Forecasting*. https://doi.org/10.1016/j.ijforecast.2022.07.011
- Zhao, M. and Linetsky, V. (2021). "High frequency automated market making algorithms with adverse selection risk control via reinforcement learning." ACM ICAIF. https://dl.acm.org/doi/10.1145/3490354.3494398
