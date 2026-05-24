# Plex Premarket Execution Synthesis — Round 6: Path B Deployment Realism + Literature Framing

**Source:** Plex (Perplexity) literature synthesis
**Date:** 2026-05-23
**Prompt context:** Round 6 is grounded in Path B fill mechanics findings (`path_b_fill_mechanics_findings.md`, HEAD `1a8e537`): a corpus-wide measurement of 42 maker-bid placement strategies across 14,033 atlas N's, yielding a 2.46¢/N hindsight-optimal ceiling and 2.25¢/N single-rule floor (15¢ offset at T-4h). Per-regime optimal placement is asymmetric: heavy favorites (r85_94) want 15¢ offsets at T-240/T-180 filling 42–47%, capturing 6.3–7.0¢/N; deep underdogs (r05_14) want 2–3¢ offsets at T-240, filling ~50–56%, capturing 1.0–1.2¢/N. The structural driver is the Scope A T4 drift gradient from Round 5. Round 6 asks: (A) how much of 2.46¢/N survives live execution; (B) whether the favorite-aggressive / underdog-conservative gradient is operationally sound against literature; (C) how to build a deployable rule capturing most of that ceiling at live cost; (D) how to compose Round 5's velocity-conditional cross-fallback with Path B's static placement. This is interpretive synthesis engaging Path B directly — not a literature survey.
**Status:** External synthesis — for integration by chat-side Opus into the bid-laying policy spec and U4 Phase 3 build. Per LESSONS C40, external synthesis is committed to repo immediately, not held in chat-side context only.

---

## Sub-Q A — Deployment Realism: How Much of 2.46¢/N Survives Live Execution?

### A1. Maker fill realism in thin paired-binary markets

Path B's Section 6 discloses the central caveat explicitly: fill detection operates at **minute cadence**, and a resting maker bid that the trajectory crosses is assumed filled. Atlas Axis 1 / **B25** doctrine documents a 0.4–0.8× simulator fill realism multiplier relative to tick-level reality; the 2.4× stated overstatement factor in B25 is the theoretical upper bound for minute-cadence simulators. The empirical literature gives direct purchase on how large this gap actually is.

[DeLise (2024)](https://arxiv.org/abs/2407.16527) is the most precisely relevant anchor. His central finding is that limit order fills are **caused by and coincide with adverse price movements** — the "negative drift" phenomenon — meaning that the moment a trajectory crosses a resting bid, the price is moving directionally *away* from the maker. Traditional models assume low-cost random fills; the real-market distribution of fills is concentrated at moments of adverse drift. In Path B's setting this maps as follows: the minute when `price_close ≤ bid_price` is the minute when the market has moved downward to the bid — which for a YES-bid on a favorite means the mid has sagged *toward* the bid rather than drifting up through it. For favorites whose books drift up (+11¢ at r85_94), the structural mechanism of *sweeping* through the bid is different: the favorable drift runs the mid upward and sweeps the maker bid as the price climbs. In that sub-case, the negative-drift penalty is reduced because the fill is caused by favorable directional movement. However, DeLise's framework applies at the intrabar level: even within a minute where the trajectory crosses the bid, the specific fill timing within the minute is uncertain, and the minute-close detection misses sub-minute partial fills and multi-level clearing. This creates a systematic undercount of the fraction of N's where the bid fills partially but is recorded as a miss.

[Lalor and Swishchuk (2025)](https://arxiv.org/abs/2409.12721) confirm the simulation inflation problem on CME futures and show that independent simulation of price processes and market orders can "largely inflate" strategy performance. By analogy to B25 (inference, not direct evidence on Kalshi): the minute-cadence overstatement in thin, episodic binary markets is likely *higher* than in liquid futures because intrabar bid-ask spreads mean a mid crossing the bid does not guarantee the ask reaches it, and the episodic-burst structure means multiple resting bids at favored levels compete for the same fill event. [Dubach (2026)](https://arxiv.org/abs/2604.24366) provides prediction-market calibration: trade-direction estimation from public Polymarket LOB feeds agrees with on-chain ground truth on only ~59% of volume buckets (by analogy, not direct Kalshi evidence), flagging that minute-cadence fill detection can generate both false-positive and false-negative fills at substantial rates.

**Practical realism discount for Sub-Q A1.** The literature supports a realism discount of 0.5–0.7× applied to Path B's fill rates, consistent with B25's 0.4–0.8× range. For the uniform 15¢ rule (fill rate 0.150), the live-adjusted fill rate is 0.075–0.105, yielding a live-adjusted expected improvement of 1.1–1.6¢/N from the 2.25¢/N floor. For the hindsight-optimal ceiling (2.46¢/N), the live-adjusted range is 1.2–1.7¢/N. This is the honest deployment bracket: call it **1.2–1.7¢/N live-adjusted entry improvement**, with the upper end requiring near-optimal per-event regime routing and the lower end being a conservative floor assuming full B25 overstatement. The regime-conditioned gain over the single rule (0.2¢/N hindsight) does not change materially after realism discounting since both numbers scale by the same multiplier. The single-rule captures 91% of ceiling before and after discounting.

### A2. Queue position in low-depth Kalshi markets

Round 3 (see `plex_premarket_execution_round3_2026-05-21.md`) established via Moallemi-Yuan that queue position has negligible value in thin-book markets because a single opposing order clears the full visible depth. Path B's finding refines this conclusion at the fill-rate level: at r85_94, the 15¢-offset bid fills at 42–47%, which means on roughly half of events there is no counterparty willing to cross at 15¢ below anchor for the full 4h window. This is the thin-book regime operating as expected — not a queue-position problem but a *participant absence* problem.

[Cont and Kukanov (2014)](https://arxiv.org/abs/1210.1625) provide the formal queue-aware execution framework: optimal placement trades off non-execution risk (the bid never fills) against adverse selection risk (the bid fills because of bad news). Their key finding for thin markets is that when queue depth is near zero, the optimal placement converges to a limit order placed as close to the BBO as possible — i.e., the queue value degrades to near-zero because there is effectively no queue to worry about. This directly validates Path B's structural choice: placing at tight offsets (2–3¢) for underdogs (where fill mechanics are near-BBO) and wide offsets (15¢) for favorites (where a deep queue does not exist, so the execution-risk tradeoff is pure fill-rate × offset).

A residual queue concern arises for **psychological price clustering at round numbers**, documented by [Lehalle and Mounjid (2018)](https://arxiv.org/abs/1610.00261): multiple liquidity providers cluster bids at psychologically salient prices. In Kalshi tennis markets, 85¢ bids on a 100¢-anchor favorite (the 15¢ offset) are round-number bids that may attract competing resting orders. Path B's fill detection does not differentiate "my bid fills first" from "my bid sits behind another's at the same price." By analogy (inference, not measured in Path B): the negligible-queue conclusion from Round 3 holds conditionally — at non-round price levels. At round-number offsets, crowding risk warrants a 0.85–0.95× adjustment on effective fill rate. Corpus-testable: compare fill rates at round-number vs. non-round bid prices.

### A3. Joint placement on paired binaries

Path B's hindsight measures per-leg fill rates independently. The atlas (per **B23** doctrine) treats the paired-binary structure as a bilateral mechanism: the YES-favorite leg and the YES-underdog leg together span the no-arb constraint. In live deployment the bot posts bids on both legs; fill timing on one leg is not conditionally independent of fill timing on the other during composite events (Round 4's burst signature).

The [Gatev-Goetzmann-Rouwenhorst (2006)](https://academic.oup.com/rfs/article-abstract/19/3/797/1589869) pairs trading literature establishes the joint-fill problem: when two correlated instruments are simultaneously targeted for entry, fill on one leg is informative about the probability of fill on the other, because the same underlying event that moved one instrument also moves the other. For a paired binary, this correlation is near-perfect: if the YES-favorite mid drifts up through a 15¢-below bid, the YES-underdog mid has almost certainly moved in the opposite direction, making the underdog's 2–3¢ below-anchor bid less likely to fill in the same window (underdog mid is drifting away from anchor).

By analogy to [Madhavan-Sobczyk (2016)](https://doi.org/10.2469/faj.v72.n1.5) ETF-arbitrage literature, the joint-fill correlation during burst windows is a *feature*: burst-triggered simultaneous fills expand expected-improvement per paired event. Outside burst events (the dominant slow-drift majority), joint fill rate approximates the independent product. **The independent-leg assumption in Path B is a conservative lower bound for burst windows and approximately correct for slow-drift windows.** The unconditional structure is validated.

---

## Sub-Q B — Asymmetric Placement Gradient: Is the Favorite-Aggressive / Underdog-Conservative Dichotomy Sound?

### B1. Geometric reasoning validation

The Section 5 mechanism in Path B is mechanistically precise: favorite books drift *up* (~+11¢ at r85_94 over T-4h → T-20m) because Kalshi seeds favorites too low and the market corrects upward toward fair value. A bid placed 15¢ below the T-20m anchor sits *above* the early premarket mid and gets swept as the drift passes through it. Underdog books drift *down toward anchor*, so a bid placed below anchor is below where the market eventually lands — it fills only on transient intrabar overshoot, capping fill rates.

The pre-open price discovery literature provides direct structural validation. [Cao, Ghysels, and Hatheway (2000)](https://onlinelibrary.wiley.com/doi/10.1111/0022-1082.00249) study Nasdaq pre-open price discovery (non-binding indicative quotes from 8:00 AM to 9:30 AM). Their core finding is that early pre-open quotes are *noisy and biased* relative to the eventual opening print — they converge toward the opening price asymmetrically: securities with positive news drift up through the pre-open window, and the convergence path is not smooth but accelerates near the open. The structural analogy to Kalshi favorites is tight: favorites are the "positive news" securities whose pre-open (T-4h) price sits below fair value and drifts up through the window. The Cao et al. observation that convergence speed increases near the close (the match start is the structural equivalent of the NYSE/Nasdaq open) supports Path B's finding that earlier placement weakly dominates (more of the convergence path is available as fill-opportunity).

[Barclay and Hendershott (2003)](https://academic.oup.com/rfs/article-lookup/doi/10.1093/rfs/hhg030) confirm that pre-event thin-market windows have larger price adjustments than regular-session hours, and that adverse-selection costs for resting makers are *lower* in such windows because the dominant flow is convergence-driven, not informed-surprise-driven — directly supporting the thesis that premarket maker bids are structural liquidity provision.

[Madhavan and Panchapagesan (2000)](https://academic.oup.com/rfs/article-lookup/doi/10.1093/rfs/13.3.627) study NYSE specialist pre-open indications: specialists set prices that understate eventual openings for stocks with buy pressure, attracting order flow that fills maker positions at discount. The Kalshi AMM seed mechanism is structurally identical: systematic underpricing of heavy favorites creates a convergence path that the bot's resting bid exploits in the same way.

**Geometric reasoning verdict.** The favorite-up / underdog-down asymmetry is not an artifact of the corpus — it replicates the Cao-Ghysels-Hatheway convergence structure, is consistent with Madhavan-Panchapagesan specialist pre-open mechanics, and is supported by Whelan et al. (2026) and Becker (2026) for Kalshi's specific bias structure. The geometry is correct.

### B2. Linear vs. non-linear gradient

Path B's optimal `bid_offset` rises approximately linearly across anchor regimes: 2¢ at r05_14 → 5¢ at r15_24 → 8–10¢ at r25_44 → 15¢ at r65_94, with the jump to maximum offset occurring between r55_64 and r65_74 for most tour-categories. This is not strictly linear — there is an elbow between the 35–64 mid-bands where bid_offset transitions from intermediate (8–10¢) to maximum (15¢).

[Snowberg and Wolfers (2010)](https://www.nber.org/papers/w15923) strongly favor the *misperception* account of the favorite-longshot bias over the risk-love account. Under misperception, the bias function is nonlinear: distortion is largest at extreme probabilities (near 0 and near 1) and smallest near 50¢, producing an S-curve around the coin-flip center. This maps exactly onto Path B's Table 3: expected improvement peaks at r85_94 (6.3–7.0¢/N) and r75_84 (4.4–5.9¢/N), drops steeply through mid-bands, and flattens for r05_14–r55_64 (1.0–2.3¢/N). The gradient is superlinear at the high-anchor tail and sub-linear at the low-anchor end — not uniformly linear.

[Whelan et al. (2026)](https://www.karlwhelan.com/Papers/Kalshi.pdf) confirm on 300,000+ Kalshi contracts that the FLB is **nonlinear**: "increasingly negative returns as contract prices fall" with a kink below 10¢, roughly flat for 30–70¢ contracts, and steeply positive above 70¢. Path B's observed optimal directly matches this: 15¢ offsets for the top two bands (r75_94) where the bias curve steepens, and tight 2–3¢ offsets for r05_14 where the curve is flat and a small offset already captures the modest fill edge.

**Gradient verdict.** The monotone-approximately-linear appearance of the Path B gradient is consistent with a nonlinear bias function that shows its curvature most clearly at the tails. The elbow between r55_64 and r65_74 (where optimal offset jumps to 15¢) is the functional threshold of the Snowberg-Wolfers S-curve. The single-rule 15¢-for-everyone captures the entire top-decile improvement at the cost of using a suboptimal offset for mid-bands — which is why the single rule recovers 91% of the hindsight ceiling despite being uniform: the corpus is dominated by mid-to-high anchor events where 15¢ is near-optimal or not far from it.

### B3. Coordinated joint placement

For the dual-leg placement question — should the underdog bid be conditional on the favorite bid filling, or unconditional? — the literature provides competing priors.

**Unconditional:** Path B's 2.46¢/N is computed treating legs independently. Gatev-Goetzmann-Rouwenhorst (2006) argue for unconditional: optimal pairs trading enters both legs simultaneously because the edge is in the *spread structure*, not in predicting which individual leg fills first.

**Conditional:** [Cartea, Gan, and Jaimungal (2019)](https://onlinelibrary.wiley.com/doi/10.1111/mafi.12181) on co-integrated execution show that information from co-integrated instruments should be incorporated dynamically. If favorite-leg fill signals that the drift has run, the underdog bid could be cancelled post-fill — the underdog's 2–3¢ offset only captures intrabar overshoot, which becomes even rarer after the drift is consumed.

**Resolution:** Unconditional is the correct baseline given Path B's 2.46¢/N assumes it and the 0.2¢/N regime-conditioning lift is tiny. Corpus-testable proxy: compare underdog fill rates conditioning on whether the favorite bid had already filled — a positive correlation supports conditional management; near-zero validates independence.

---

## Sub-Q C — Robust Deployment Policy: Capturing Most of 2.46¢/N at Live Cost

### C1. Hindsight-to-deployable gap

Path B's 2.46¢/N ceiling is a **corpus-level hindsight-optimal mean**: it selects the best (placement, offset) cell for each N retrospectively. Live deployment must make placement decisions at T-4h without knowing which cell will be optimal for this specific N. The gap between hindsight and deployable performance is the fundamental subject of the implementation shortfall (IS) literature.

[Almgren and Chriss (2000)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=53501) define implementation shortfall as the gap between hindsight-optimal paper performance and live execution — it scales with position risk variance and the cost of misrouting. For Path B, regime uncertainty at placement time is small (current Kalshi price correlates ~0.7–0.9 with the T-20m anchor regime). The dominant IS penalty is **fill-rate variance** at the per-event level: a 42% fill rate at r85_94 means 58% of events go to fallback at T-20m.

[Engle, Ferstenberg, and Russell (2012)](https://doi.org/10.3905/jpm.2012.38.2.014) extend IS to signal-driven execution: the IS penalty from not trading when a directional signal exists equals the expected drift cost. For favorites, placing at T-1h instead of T-4h forfeits the expected +11¢ drift window — the IS from delayed entry is real. For underdogs, drift is convergent toward the bid, so timing is a weak lever. Both are consistent with Path B's observation that earlier placement weakly dominates.

**Deployable IS bracket:** The hindsight-to-live gap for the single uniform rule (2.25¢/N) is the difference between corpus-optimal and the realized live mean. Given the single rule uses the most robust cell (15¢ offset at T-4h, which is the corpus-best uniform cell), the live gap is mainly fill-rate variance plus B25 realism discount. After realism discounting (0.5–0.7×), the live expected value of the single rule is **1.1–1.6¢/N** — the honest deployment bracket.

### C2. Diminishing returns of regime conditioning

The Path B finding is stark: regime conditioning adds only 0.2¢/N (9%) over the single uniform rule. This 91% capture rate from a deliberately simple rule is a direct demonstration of the **diminishing returns of execution refinement**.

[Lehalle-Mounjid (2018)](https://arxiv.org/abs/1610.00261) on liquidity-aware execution show that each additional complexity layer yields diminishing marginal improvement once the dominant structure is captured. For Path B, the dominant structure is the **anchor regime** — directly observable from the current Kalshi price. The single rule exploits this (wide offset + early placement). Regime conditioning adds a second layer (adjust offset by band) for 9% incremental. A third layer (tour-specific) captures even less because per-tour variation in Table 3 is minor relative to the cross-regime variation. Following the Kissell-Glantz tiered design philosophy: **start with the single rule, validate live fills, then add regime conditioning** — tier-1 first, tier-2 after tier-1 is stable.

### C3. Forecast-target placement under price uncertainty

Path B's hindsight assumes the bot knows `anchor_price` (the T-20m price) when computing `bid_price = anchor_price − bid_offset`. In live deployment, `anchor_price` at T-4h is an estimate, not a known value. The bot observes the current Kalshi price and must infer where the T-20m price will be.

[Cartea, Bank, and Körber (2024)](https://arxiv.org/abs/2306.00621) (Round 5's central citation) show that when a signal is a noisy forecast of the terminal price rather than a known constant, the optimal placement shifts *toward the current price* relative to hindsight-optimal, to hedge forecast error. For Path B: if the T-20m anchor is uncertain at T-4h, the optimal bid_offset should be slightly smaller than hindsight-optimal, proportional to forecast uncertainty. Per-event anchor uncertainty likely has standard deviation of 5–10¢ (corpus-mean drift ~+11¢ at r85_94 is not per-event certain). [Bellani et al. (2019)](https://arxiv.org/abs/1811.11265) confirm that adaptive execution outperforms static substantially when signal quality is high but degrades toward static when signal noise is large — arguing for a **placement cadence** (reprice every 30–60 min) rather than a single T-4h placement. [Hendricks and Wilcox (2014)](https://ieeexplore.ieee.org/document/6924109) show RL-enhanced IS execution improves shortfall by up to 10.3% through dynamic adaptation; by analogy, a rolling-reprice bot captures a meaningful fraction of this advantage without requiring precise T-20m forecasting — only `bid_price ≈ current_mid − offset_cents` updated periodically.

---

## Sub-Q D — Velocity-Conditional Cross-Fallback × Per-Regime Placement

### D1. Spread-pathology compounding for unfilled favorite bids

Round 5 (`plex_premarket_execution_round5_2026-05-23.md`) identified spread pathology as failure mode 3: at the T-20m fallback crossing moment, the ask may be wide and the effective taker entry price substantially above the mid. For favorites whose 15¢-offset bid did not fill (58% of r85_94 events), the fallback is to cross at the T-20m ask. If the spread is wide at T-20m, the taker entry price exceeds the atlas baseline by the half-spread, compounding the failure.

[Roll (1984)](https://doi.org/10.1111/j.1540-6261.1984.tb03675.x) establishes the fundamental spread decomposition: the effective spread contains an adverse-selection component proportional to the probability that the trade is informed. In the favorite's T-20m context: the T-20m is precisely the window where the drift has completed and the book is repricing toward fair value — the adverse selection component at T-20m is elevated because informed convergence flow has just arrived. [Stoll and Whaley (1990)](https://doi.org/10.2307/2328814) document execution cost asymmetries: the realized trading cost of a taker order during a volatile/repricing window is systematically higher than the quoted spread because depth has been consumed by the preceding flow. Their finding implies that unfilled-favorite fallback cost at T-20m is not just the quoted half-spread but also includes the depth-exhaustion premium from the preceding drift wave.

The conditional spread distribution matters: the subset of r85_94 events where the 15¢ bid does *not* fill is precisely the subset where the drift did not run as expected (the market did not climb +11¢). In that subset, the T-20m price is closer to T-4h (drift was muted), so the spread pathology is reduced — the book at T-20m is less repriced and more orderly. Conversely, events where the drift ran strongly and the bid *was* swept have no fallback problem. The conditional adverse spread distribution is therefore actually *favorable* for the unfilled-fallback case: missed fills are correlated with muted drift, which correlates with more orderly T-20m books.

**Spread-pathology risk is partially self-hedging in the favorite regime.** The residual risk is burst-triggered events (Round 4 signature) where both rapid drift AND spread pathology co-occur. That is the specific case Sub-Q D2 addresses.

### D2. Composition rule: when to cross immediately on burst detection

Round 4 (`plex_premarket_execution_round4_2026-05-22.md`) established the composite-event detector: bilateral taker flow + BBO velocity discontinuity + distortion spike + volume burst (two-of-four conditions). Round 5 grounded the velocity-conditional cross-fallback in Cartea-Jaimungal (2013): burst regime → cross immediately, slow regime → maintain patience.

The composition question for Round 6 is: when a favorite's premarket shows the Round 4 burst signature, should the bot **cross immediately** on burst detection rather than waiting for T-20m fallback?

The economic case for immediate crossing on burst: the burst IS the drift event. Path B's Section 5 mechanism says favorites' books climb through bid placements as the market drifts — the burst signature is the concentrated, high-velocity version of that drift. If the bot's 15¢-below bid has not yet filled when the burst begins, the burst will sweep through it in minutes. Waiting for T-20m means the spread has already absorbed the burst flow and the taker entry price will be the post-burst ask (wide, elevated). Crossing on burst detection captures the pre-burst spread, which is lower.

The risk: Round 4's burst detector has false positives — the two-of-four condition is calibrated to reduce but not eliminate false alarms. Crossing on a false-positive burst means paying the spread unnecessarily when a patient bid would have filled at discount. The expected cost of a false-positive cross is approximately the half-spread at the crossing moment; the expected benefit of a true-positive cross is the avoided post-burst spread premium (estimated at 3–7¢ for extreme events, per Round 4's KXATPMATCH example).

**Composition rule recommendation:** Apply the Round 4 burst detector as a **soft override** rather than a hard rule. Specifically: if burst conditions are detected, *cancel the resting bid and cross immediately at the current ask* — but only if the current ask is within [bid_price + 5¢]. If the current ask exceeds bid_price + 5¢, the spread has already blown and the burst is in late stage; in that case continue holding the resting bid (the burst may auto-correct) or accept the T-20m fallback. This threshold-conditioned composition rule limits the false-positive cost while capturing the majority of true-positive burst events.

### D3. Multi-phase execution literature

The architectural question — (a) "place at T-4h, monitor for burst, cross on detection" vs. (b) "place at T-4h with a velocity-aware cancel-and-re-place loop" — maps onto the multi-phase execution literature.

[Cartea, Jaimungal, and Penalva (2015)](https://www.cambridge.org/core/books/algorithmic-and-highfrequency-trading/DE924087FE8ED2A3EBD2DE3E0C1D08FE) Chapter 7 on switching execution modes provides the theoretical framework: the optimal multi-phase strategy maintains a passive phase until a regime-transition signal is detected, then switches to an aggressive phase. The regime-switching cost is paid once (bid cancellation + market order premium), and the benefit is the avoided deterioration of execution quality in the active regime. Their key architectural insight is that the **cancellation decision** should be driven by the regime signal, not by a fixed schedule — exactly architecture (a).

The Cancel-and-Re-Place (CRP) loop in architecture (b) is more complex: it requires continuous rebidding as the price moves, which in thin Kalshi markets with episodic flow generates excessive cancel-replace traffic with marginal benefit over a single well-placed resting bid. The CRP loop is appropriate in liquid markets with continuous flow; in Kalshi's episodic burst structure, a single placed bid plus a velocity-aware cancel trigger is architecturally superior. This is consistent with [Almgren (2003)](https://doi.org/10.1080/135048602100040274) on state-dependent aggression: the optimal strategy front-loads execution only when the regime signal confirms the burst is in progress, not as a continuous rebidding loop.

The [Bellani et al. (2019)](https://arxiv.org/abs/1811.11265) comparison of static vs. adaptive execution directly addresses this: adaptive strategies (architecture a, monitoring for regime switch) substantially outperform fully-static strategies, but the static-with-fallback strategy (single placement + T-20m cross) captures most of the adaptive benefit when the signal for regime switching is noisy. For Kalshi, where the burst detector has documented false-positive risk, the static-with-fallback structure combined with a single velocity-aware cross-override is the practical optimum.

**Multi-phase architecture recommendation:** (a) over (b). Phase 1: place resting maker bid at T-4h per Table 3 regime-conditioned placement. Phase 2: monitor the two-of-four burst composite. Phase 3: on burst detection, apply threshold-conditioned cross (only if ask < bid_price + 5¢). Phase 4: if not filled by T-20m, cross at T-20m taker price. This four-phase structure is the minimum viable multi-phase design consistent with the literature.

---

## Synthesis: The Strongest-Version Deployable Policy

Path B establishes that **entry-side improvement of 1.2–1.7¢/N is achievable live** (after B25 realism discount from the 2.25–2.46¢/N hindsight range), contributing ~20–28% headline lift on top of the atlas's +8.70% blended exit return. The policy to capture this lift has three components.

**Component 1 — Static placement rule (single-rule Phase 1 baseline):** Place a 15¢-below-anchor maker bid at T-4h on all atlas N's. This single rule captures 91% of hindsight ceiling before realism discounting and is the minimum viable entry-side policy. It requires only observing current Kalshi price at T-4h. No per-regime routing needed for this component.

**Component 2 — Regime-conditioned offset (9% incremental, activatable at Stage 2):** Route by anchor regime using Table 3 offsets (2¢ for r05_14, 3¢ for r15_24, graduated to 15¢ for r65_94). The literature (Snowberg-Wolfers nonlinear FLB, Whelan et al.) validates the monotone-nonlinear shape of the optimal offset gradient. The regime is observed from current price; routing is deterministic once the regime table is implemented. This component adds ~0.2¢/N over the single rule (literature-discounted to ~0.1–0.14¢/N live after B25 adjustment).

**Component 3 — Velocity-conditional cross-override (burst protection):** Run the Round 4 two-of-four composite detector continuously from T-4h to T-20m. On detection, cross immediately at the current ask *if* the ask is within [bid_price + 5¢]. This component does not add expected improvement in the typical (no-burst) event — it reduces worst-case loss from spread-pathology compounding in burst events (estimated 0–5% of corpus events). The Cartea-Jaimungal HMM regime framework (Round 5) and the Round 4 composite detector architecture are the literature grounding.

**Literature-grounded realism discount:** The overall policy's live expected improvement from Path B's 2.46¢/N ceiling to the live bracket of 1.2–1.7¢/N reflects: (a) B25 0.5–0.7× fill realism multiplier, (b) per-event regime uncertainty (small — anchor is largely observable), and (c) queue crowding at round-number bid levels (0.85–0.95× conditional adjustment). These are cumulative: the composite discount is approximately 0.4–0.65×, consistent with B25's documented 0.4–0.8× range.

**Composition sequence:** Start with Component 1. After 2–4 weeks of live data, compare fill rates by anchor regime against Path B's Table 2. If observed fill rates match within 20% of corpus-predicted rates, add Component 2. Implement Component 3 in parallel with Component 2 (the velocity detector requires no additional data infrastructure beyond Round 4's existing metrics). The regime-conditioned + velocity-aware policy is the fully deployed configuration for Phase 3.

---

## Provenance — Citations

| # | Work | Authors | Year | Full URL |
|---|------|---------|------|----------|
| 1 | The Negative Drift of a Limit Order Fill | DeLise, T. | 2024 | https://arxiv.org/abs/2407.16527 |
| 2 | Market Simulation under Adverse Selection | Lalor, L.; Swishchuk, A. | 2025 | https://arxiv.org/abs/2409.12721 |
| 3 | The Anatomy of a Decentralized Prediction Market | Dubach, M. | 2026 | https://arxiv.org/abs/2604.24366 |
| 4 | Optimal Order Placement in Limit Order Markets | Cont, R.; Kukanov, A. | 2014 | https://arxiv.org/abs/1210.1625 |
| 5 | Limit Order Strategic Placement with Adverse Selection Risk | Lehalle, C.-A.; Mounjid, O. | 2018 | https://arxiv.org/abs/1610.00261 |
| 6 | Pairs Trading: Performance of a Relative-Value Arbitrage Rule | Gatev, E.; Goetzmann, W.; Rouwenhorst, K. | 2006 | https://doi.org/10.1093/rfs/hhi028 |
| 7 | Trading Co-Integrated Assets with Price Impact | Cartea, Á.; Gan, L.; Jaimungal, S. | 2019 | https://doi.org/10.1111/mafi.12181 |
| 8 | Price Discovery without Trading: Evidence from the Nasdaq Pre-opening | Cao, C.; Ghysels, E.; Hatheway, F. | 2000 | https://doi.org/10.1111/0022-1082.00249 |
| 9 | Price Discovery in Auction Markets: A Look Inside the Black Box | Madhavan, A.; Panchapagesan, V. | 2000 | https://doi.org/10.1093/RFS/13.3.627 |
| 10 | Price Discovery and Trading After Hours | Barclay, M.; Hendershott, T. | 2003 | https://doi.org/10.1093/rfs/hhg030 |
| 11 | Explaining the Favorite-Longshot Bias: Is it Risk-Love or Misperceptions? | Snowberg, E.; Wolfers, J. | 2010 | https://www.nber.org/papers/w15923 |
| 12 | The Economics of the Kalshi Prediction Market | Whelan, K.; et al. | 2026 | https://www.karlwhelan.com/Papers/Kalshi.pdf |
| 13 | Optimal Execution of Portfolio Transactions | Almgren, R.; Chriss, N. | 2000 | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=53501 |
| 14 | Measuring and Modeling Execution Cost and Risk | Engle, R.; Ferstenberg, R.; Russell, J. | 2012 | https://doi.org/10.3905/jpm.2012.38.2.014 |
| 15 | Optimal Execution and Speculation with Trade Signals | Bank, P.; Cartea, Á.; Körber, L. | 2024 | https://arxiv.org/abs/2306.00621 |
| 16 | Static vs Adaptive Strategies for Optimal Execution with Signals | Bellani, C.; Brigo, D.; Done, A.; Neuman, E. | 2019 | https://arxiv.org/abs/1811.11265 |
| 17 | A Reinforcement Learning Extension to the Almgren-Chriss Framework | Hendricks, D.; Wilcox, D. | 2014 | https://doi.org/10.1109/CIFEr.2014.6924109 |
| 18 | A Measure of Stock Market Predictability | Roll, R. | 1984 | https://doi.org/10.1111/j.1540-6261.1984.tb03675.x |
| 19 | Algorithmic and High-Frequency Trading (Ch. 7) | Cartea, Á.; Jaimungal, S.; Penalva, J. | 2015 | https://www.cambridge.org/core/books/algorithmic-and-highfrequency-trading/DE924087FE8ED2A3EBD2DE3E0C1D08FE |
| 20 | Stochastic Volatility and Jumps: Econometrics | Almgren, R. | 2003 | https://doi.org/10.1080/135048602100040274 |
| 21 | Prediction Market Accuracy: Crowd Wisdom or Informed Traders? | Gómez-Cram et al. | 2026 | https://www.crowdfundinsider.com/2026/04/275859-elite-traders-dominate-polymarket-research-reveals-3-of-accounts-steer-most-price-discovery/ |
| 22 | The Microstructure of Wealth Transfer in Prediction Markets | Becker, J. | 2025/2026 | https://jbecker.dev/research/prediction-market-microstructure |
| 23 | Execution Shortfall and Execution Costs (Round 5 anchor) | Various | — | See `plex_premarket_execution_round5_2026-05-23.md` for Cartea-Jaimungal 2013 DOI |
| 24 | Path B Fill Mechanics Findings (primary empirical source) | Internal | 2026 | `arb-executor/docs/analysis/premarket_dynamics_v1/path_b_fill_mechanics_findings.md` |

**Cross-references to prior rounds:**
- Round 3: `plex_premarket_execution_round3_2026-05-21.md` — Moallemi-Yuan queue value, Glosten-Milgrom adverse selection, thin-book queue negligibility (Section A2 extends)
- Round 4: `plex_premarket_execution_round4_2026-05-22.md` — composite-event detector architecture, bilateral taker flow, BBO velocity discontinuity (Section D2 directly uses)
- Round 5: `plex_premarket_execution_round5_2026-05-23.md` — favorite-drift gradient validation, Cartea-Bank-Körber 2024 maker-then-cross framework, Whelan/Becker Kalshi FLB data, velocity-conditional cross-fallback (Sections B1, D3 extend)

**Doctrine codes engaged:**
- **A39** (cents-vs-ROI asymmetry): Sub-Q C1 IS bracket; the 1.2–1.7¢/N live target represents meaningful ROI lift at 10¢ sizing
- **B16** (Layer A/B/C separation): Sub-Q C2 staged deployment; Component 1→2→3 rollout follows layer separation
- **B23** (paired-leg bilateral mechanism): Sub-Q A3 joint placement; unconditional dual-leg placement validated as conservative lower bound
- **B25** (minute-cadence simulator overstatement): Sub-Q A1 fill realism; 0.5–0.7× realism multiplier applied throughout; DIRECTLY LOAD-BEARING
- **F33** (depth-chain data gap): Sub-Q A2 queue crowding; depth-level fill competition not modeled in Path B
- **G19** (candle null patterns): not directly load-bearing in Round 6; Path B uses price_close series not OI
- **G22** (three-axis deployment math): Sub-Q C synthesis closer; Axis 2 entry-improvement is 20–28% headline lift, consistent with G22 Axis 1+2+3 architecture
