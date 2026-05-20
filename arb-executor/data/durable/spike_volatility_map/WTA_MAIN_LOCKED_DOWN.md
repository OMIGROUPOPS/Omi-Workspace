# WTA_MAIN descriptive lock-down

Hindsight-optimal per-cell exit-or-hold rules across 3,683 WTA_MAIN N's, 10-month corpus (2025-06-18 to 2026-04-30, 248 trading days), 10ct sizing, taker-floor T-20m anchors. Same methodology as ATP_MAIN (commit 481de7f), Plex-confirmed in round 4 dialogue. Doctrine-aligned (A21/A39/B13/B16/B18/E32/E32(e)/G22).

## Headline numbers — three resolutions

| Width | n_cells | Total $    | Capital     | ROI%   | Negative cells | Hold cells |
|-------|---------|------------|-------------|--------|----------------|------------|
| 1c    | 90      | +$1,824.90 | $18,545.90  | +9.84% | 14             | 10         |
| 2c    | 45      | +$1,223.90 | $18,545.90  | +6.60% | 8              | 3          |
| 3c    | 30      | +$987.60   | $18,545.90  | +5.33% | 7              | 3          |

## Daily framing

Average trading day: 14.85 N's, $74.78 capital deployed, $7.36 earnings → +9.84% per-N average ROI on cycling capital.

## Regime breakdown (1c resolution)

| Regime | Anchor range | Capital  | Total $   | ROI%    |
|--------|--------------|----------|-----------|---------|
| Cheap  | 5–30c        | $1,620   | +$700.00  | +43.22% |
| Mid    | 31–65c       | $8,568   | +$830.80  | +9.70%  |
| High   | 66–94c       | $8,358   | +$294.10  | +3.52%  |

Cheap cells deploy 9% of capital and generate 38% of dollar profit. A39 cent-sensitivity geometry holds.

## Cross-category comparison vs ATP_MAIN

| Metric              | ATP_MAIN        | WTA_MAIN        |
|---------------------|-----------------|-----------------|
| Total N             | 4,137           | 3,683           |
| Trading days        | 252             | 248             |
| 1c total $          | +$1,658.80      | +$1,824.90      |
| 1c ROI              | +7.90%          | +9.84%          |
| 3c ROI              | +4.88%          | +5.33%          |
| Cheap regime ROI    | +36.13%         | +43.22%         |
| Mid regime ROI      | +7.45%          | +9.70%          |
| High regime ROI     | +3.11%          | +3.52%          |
| Hold cells (1c)     | 8               | 10              |
| Negative cells (1c) | 15              | 14              |
| Avg N / trading day | 16.42           | 14.85           |
| Avg daily ROI       | +7.90%          | +9.84%          |

WTA_MAIN structurally tracks ATP_MAIN at the descriptive-corpus level: same shape (cheap dominates, mid contributes, high underperforms), similar hold/negative cell counts. WTA_MAIN runs slightly hotter per-trade (+1.94pp ROI) despite lower volume (-1.5 N/day), translating to +$0.78/day more earnings on similar capital. Codebase hint that ATP/WTA require structurally different strategies is not visible in the spike-volatility map; any tour difference lives in execution mechanics (depth, spread, fill behavior), not corpus volatility structure.

## Deployment rule

Trade all 90 cells per the locked checklist (wta_main_descriptive_1c.parquet). Same operational philosophy as ATP_MAIN: volume is the constraint; Tier 3 marginal cells are execution-bound, not strategy-bound; Tier 4 (negative cells) is acceptable drag.

## Methodology

Identical to ATP_MAIN_LOCKED_DOWN.md methodology section (commit 481de7f). 1c/2c/3c non-overlapping cells, hindsight-optimal per-cell exit-or-hold, capital = anchor_price × N × 10ct in dollars, ROI = best_sum / capital * 100.

## Three-axis caveat

AXIS 1 — Exit-side fill realism (pushes DOWN). 0.4-0.8x of simulated, B25/Cat-11 evidence, pending Layer C.
AXIS 2 — Entry-side maker improvement (pushes UP). ~+10-30% on the headline, pending dedicated measurement. Tier 3 marginal cells are most levered to entry-side improvement.
AXIS 3 — Arrival frequency (G22). Frequency observable (14.85 N/day at 10ct); sizing depends on depth (F33).

## What this is NOT

- NOT a predictive rule (descriptive measurement only).
- NOT deployable dollars (three-axis caveat between this and realized PnL).
- NOT a single "correct" number — three resolutions are honest descriptions at three cell granularities.

## State after this commit

ATP_MAIN: LOCKED (commit 481de7f). WTA_MAIN: LOCKED (this commit). ATP_CHALL / WTA_CHALL: pending — same methodology to apply.

Combined ATP+WTA Main operational picture: ~31 N's/day, ~$158 capital/day, ~$14 earnings/day, ~+8.8% combined daily ROI on cycling capital at 10ct sizing.
