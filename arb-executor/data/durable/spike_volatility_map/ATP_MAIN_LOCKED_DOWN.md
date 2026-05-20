# ATP_MAIN descriptive lock-down

Hindsight-optimal per-cell exit-or-hold rules across 4,137 ATP_MAIN N's, 10-month corpus (2025-06-18 to 2026-05-01, 252 trading days), 10ct sizing, taker-floor T-20m anchors. Plex-confirmed methodology in round 4 dialogue; doctrine-aligned (A21/A39/B13/B16/B18/E32/E32(e)/G22).

## Headline numbers — three resolutions

| Width | n_cells | Total $    | Capital     | ROI%   | Negative cells |
|-------|---------|------------|-------------|--------|----------------|
| 1c    | 90      | +$1,658.80 | $21,003.40  | +7.90% | 15             |
| 2c    | 45      | +$1,245.20 | $21,003.40  | +5.93% | 9              |
| 3c    | 30      | +$1,025.50 | $21,003.40  | +4.88% | 5              |

The three resolutions answer slightly different questions at different cell granularities. Per Plex, neither is "more correct" — they describe what the corpus would have paid under per-cell hindsight-optimal exit-or-hold rules at three resolutions of cell definition.

## What the 1c→3c gap measures

The $633 gap between 1c and 3c is two things mixed together:
- **Over-optimization tax:** per-cell argmax overfitting to within-cell noise at small N (~46 N/cell at 1c).
- **Real cell-by-cell heterogeneity:** adjacent 1c cells genuinely want different exits in some regions, particularly the cheap regime per A39 cent-sensitivity geometry.

The 2c probe (commit pending in this same atlas) showed pooling adjacent 1c cells DESTROYED edge in two specific cases: pooling cells 37 (+$42, X=39c) and 38 (-$12.60, X=1c) into [37,39) produced -$8.10 (constituent sum was +$29.40, net cost $37.50). This is direct evidence that some of the 1c-vs-3c gap is real heterogeneity that pooling destroys, not pure over-optimization.

## Daily framing

Average trading day: 16.4 N's, $83 capital deployed, $6.58 earnings → +7.9% per-N average ROI on cycling capital. Compounding is intraday (trades settle same day, capital re-uses for next day's trades). Scale-up via ct-per-N sizing is downstream (G22 axis, F33 depth gap).

## Regime breakdown (1c resolution)

| Regime | Anchor range | Capital  | Total $   | ROI%   |
|--------|--------------|----------|-----------|--------|
| Cheap  | 5–30c        | $1,736   | +$627.20  | +36.1% |
| Mid    | 31–65c       | $9,959   | +$742.10  | +7.5%  |
| High   | 66–94c       | $9,308   | +$289.50  | +3.1%  |

Cheap cells deploy 8% of capital and generate 38% of dollar profit. A39 geometry confirmed empirically: 1c of price movement at 7c entry = 14% ROI; same 1c at 90c = 1% ROI; cheap regime accordingly carries the corpus on ROI terms.

## Deployment rule

Trade all 90 cells per the locked checklist (atp_main_descriptive_1c.parquet). Volume is the operational constraint; cherry-picking to high-ROI cells alone leaves 9 N's/day instead of 16 and limits statistical smoothing of variance. Tier 3 marginal cells stay in the deployment — they are execution-bound, not strategy-bound (see Three-Axis Caveat AXIS 2). Tier 4 (cells 38 and 93) are 2% of corpus, $28 of drag; trade them to maintain volume, accept as cost of doing business.

## Methodology

- **Cells:** 1c-wide bins (round(anchor_price*100)) or 2c/3c-wide non-overlapping bins starting at 5c.
- **Per-cell rule:** sweep every reachable exit target +X cents (X capped at 99-anchor_cents). For each cell, pick the X that maximizes sum$10ct across that cell's N's. If no X beats hold-to-settlement, the cell rule is "hold to 99c on winners / 1c on losers."
- **Per-N payoff:** spike (the price chart visibly running up after entry) reaches +X cents with at least 250ct of size at that level → realize +X cents. Otherwise hold to settlement: winner = +(99-anchor), loser = -(anchor-1).
- **Capital deployed per cell:** sum across cell's N's of anchor_price × 10ct in dollars. ROI = best_sum$ / capital_deployed$.
- **All N's appear in exactly one cell per resolution (no double-counting).** Corpus totals are sums across cells per resolution.

## Three-axis caveat

AXIS 1 — Exit-side fill realism (pushes DOWN). Every simulated +X exit assumes any qualified-size taker print at that level = guaranteed maker fill. B25/Cat-11 evidence: 2.4x simulator overstatement of fill rates for limit policies in minute-cadence simulators against tick-level reality. Our >=250ct size-qualification floor and ATP_MAIN deep mid-match liquidity mitigate this somewhat. Expected realized capture: 0.4-0.8x of simulated, pending dedicated Layer C fill-realism work.

AXIS 2 — Entry-side maker improvement (pushes UP). Every anchor is a real T-20m taker trade — someone who paid up to cross the spread. A resting maker buy at the bid (or better) fills at a BETTER price than the taker print. On typical ATP_MAIN spreads this is ~1c per ct cheaper entry per trade, compounding across larger captures on hits, higher ROI per hit, smaller losses on misses. Expected improvement: ~+10-30% on the headline, pending dedicated entry-execution measurement. Aligns with the bot's existing edge thesis (LESSONS line 48: anchor-relative discount capture, 97% of fills Scenario C_discount). The Tier 3 marginal cells (~35 cells where best_X is small) are the cells most levered to entry-side improvement.

AXIS 3 — Arrival frequency (G22). Deployable economics need N's/day × ct/N sizing. Frequency observable (16.4 N/day at 10ct); sizing depends on depth (F33).

## What this is NOT

- NOT a predictive rule. The IS/OOS chronological time-split test on this corpus showed per-cell argmax fits do not generalize forward at any tested smoothness penalty. The descriptive measurement and the predictive question are explicitly separated — both can be true: the corpus produced this hindsight-optimal P&L, AND fitting that P&L's specific exit choices to one time half does not predict the other half. The descriptive number describes what was; it does not claim what will be.
- NOT deployable dollars. Three axes between this number and realized PnL.
- NOT a single "correct" number — three resolutions are honest descriptions at three cell granularities.

## Open enhancements (deferred, not blocking)

Adaptive-width binning (variable cell width across the anchor spectrum, with pre-specified similarity thresholds). Plex-recommended approach: tight/medium/loose threshold grid for sensitivity transparency. Best run AFTER the four-category atlas is locked so adaptive band-width patterns can be compared across categories (e.g., does the 5-30c cheap region consistently want 1c bands across ATP Main / WTA Main / ATP Chall / WTA Chall?). Not blocking on the descriptive deliverable.

## State after this commit

ATP_MAIN descriptive measurement: LOCKED. WTA_MAIN, ATP_CHALL, WTA_CHALL: pending — identical methodology to apply sequentially.
