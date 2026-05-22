# Plex External Synthesis — Round 1
## Literature on Premarket Execution in Structurally-Coupled Binary Markets

**Date:** 2026-05-21  
**Context:** OMI Group Holdings / Kalshi tennis binary YES/NO paired-contract strategy. Atlas anchored at T-20m; this synthesis informs premarket maker-bid placement policy for the U4 Phase 3 build.

---

## 1. Market-Making in Paired Binaries with a Known No-Arb Sum Constraint

### 1.1 The Constraint Structure

Kalshi tennis YES/NO paired contracts are structurally equivalent to a **complete binary partition**: P(YES) + P(NO) = 1.00, so at fair value the cent-denominated bid-sum from maker quotes should sum to ≤ 100c and the ask-sum to ≥ 100c. The `paired_arb_gap_maker` = 1.00 − (own_bid + partner_bid) is therefore a direct signed measure of the *maker-side slack* relative to the no-arb bound. This is not an independent-asset market-making problem; it is structurally analogous to:

- **Options put-call parity pairs** (put + call on same strike = discounted forward), where the parity bound constrains joint quoting
- **Binary prediction market pairs** in play-money and real-money platforms (PredictIt YES+NO ≈ 100c minus vig; Iowa Electronic Markets winner-takes-all dual contracts)
- **Sum-constrained futures legs** (e.g., calendar spread microstructure where leg A + leg B = spot)

### 1.2 Relevant Academic Literature

**Prediction market microstructure — paired/complete-set contracts:**
- *Hanson (2003, "Combinatorial Information Market Design," Information Systems Frontiers)* introduced the Logarithmic Market Scoring Rule (LMSR), which explicitly prices all outcomes jointly and enforces the probability-sum constraint at the market-maker level. The implication for an alpha-capture strategy operating against an LMSR-like book is that the *book's own liquidity function* creates mechanical reversion of any sum-distortion above zero because the automated market maker will always offer the complementary leg at 100c − quote.
- Kalshi operates a *central limit order book* (CLOB), not LMSR — so the sum constraint is *not* enforced by a market maker. Instead it is enforced by arbitrageurs. This is the key structural fact for the operation: the `paired_arb_gap_maker` gap persists until an arbitrageur closes it, and that persistence window is the opportunity.
- *Wolfers & Zitzewitz (2004, "Prediction Markets," JEP)* and *Manski (2006, "Interpreting the Predictions of Prediction Markets," Economics Letters)* discuss the relationship between posted prices and true probabilities in binary markets with constrained sums. The key insight: in thin markets, bid-ask spreads mean that a simultaneous YES+NO purchase at taker prices may cost >100c even when fair-value sum = 100c, so distortion is normal and its magnitude tracks liquidity.
- *Abramowicz (2007, "Prediction Markets and Legal Compliance")* documents the structural relationship between paired-contract pricing and the market's aggregate belief calibration. For correlated-leg markets, the cross-leg information linkage means that price updates on one leg should mechanically update the fair-value anchor of the partner leg.

**Options-pair / correlated-leg market making:**
- *Glosten & Milgrom (1985, "Bid, Ask and Transaction Prices in a Specialist Market")* — the foundational adverse-selection model. In a paired market, the market maker on one leg must condition on the informational content of the partner leg's order flow, since both legs resolve to the same event. The effective spread on each leg embeds the adverse selection risk for both legs jointly.
- *Garman (1976)* and the subsequent market-making literature assume independent inventory positions, but for paired binary contracts, inventory on leg A is perfectly negatively correlated with the hedge provided by leg B. This creates an unusual structure: a maker who holds both legs simultaneously has *zero event risk* (they collect 100c on settlement regardless of outcome) but faces *price-movement risk* on unrealized marks and *liquidity risk* if one leg fills and the other doesn't.
- *Stoikov & Saglam (2009, "Option Market Making Under Inventory Risk," Review of Derivatives Research)* extend the Avellaneda-Stoikov framework to options pairs, directly applicable here: the maker's optimal quote on each leg should account for the delta/gamma exposure across both legs jointly, not independently.

### 1.3 Structural Implication for the Operation

The operation is **not a market maker in the Glosten-Milgrom sense** — it does not provide two-sided quotes continuously. It is placing *one-sided maker bids* with directional intent (wanting fills at favorable prices). The paired-structure benefit is that the `paired_arb_gap_maker` feature is a *pre-fill screening signal*: bids placed when the gap is large (sum is far from 100c) have a higher probability of being on the favorable side of the no-arb bound's eventual convergence. The paired constraint creates a gravity toward 100c that is absent in unconstrained single-asset markets.

---

## 2. Premarket / Pregame Price Discovery Dynamics

### 2.1 Spread and Depth Evolution as Time-to-Event Decreases

The premarket microstructure of binary event contracts has been studied most rigorously in:

- **Horse racing / parimutuel markets:** *Crafts (1985, "Some Evidence of Insider Knowledge in Horse Race Betting in Britain")* and *Shin (1993, "Measuring the Incidence of Insider Trading in a Market for State-Contingent Claims")* show that in fixed-odds sports markets, spreads narrow and informational efficiency increases as post time approaches. The "longshot bias" (over-pricing of low-probability outcomes) diminishes near post because sharp money with superior information enters late and corrects prices.
- **Prediction markets temporal dynamics:** *Tetlock (2004)* and *Berg, Nelson & Rietz (2008, "Prediction Market Accuracy in the Long Run," International Journal of Forecasting)* document that prediction market prices converge to true probabilities monotonically as event-resolving information is revealed. For sports events, the primary information arrival is: (a) line movement on tier-1 books (Pinnacle), (b) injury/roster news, (c) pre-match warm-up signals.
- **Sports betting premarket:** *Levitt (2004, "Why Are Gambling Markets Organised So Differently from Financial Markets?")* and *Sauer (1998, "The Economics of Wagering Markets")* establish that NFL/NBA point spreads at opening are systematically less efficient than closing lines; spread compression over the premarket window is well-documented. Tennis markets, being less liquid and more episodic, likely show larger spread compression windows.

### 2.2 Phases of Premarket Microstructure

Based on the literature and the structural characteristics of Kalshi tennis books, premarket microstructure likely exhibits **three phases**, consistent with the "formation/stable" regime split observed in the OMI dataset:

| Phase | Approximate Window | Characteristics |
|---|---|---|
| Formation | T−∞ to T−2h | Wide spreads, thin depth, local book dominates. Large `paired_arb_gap_maker`. High mean-reversion speed. |
| Convergence | T−2h to T−20m | Tier-1 books (Pinnacle) begin setting, market-wide consensus forms. Spread compression. Gap narrows. |
| Crystallization | T−20m to T=0 | Spreads near minimum, dept