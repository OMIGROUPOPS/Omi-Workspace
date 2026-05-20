# ATP_CHALL descriptive lock-down

Hindsight-optimal per-cell exit-or-hold rules across 5,326 ATP_CHALL N's, corpus (2026-01-13 to 2026-05-01, 109 trading days), 10ct sizing, taker-floor T-20m anchors. Same methodology as ATP_MAIN/WTA_MAIN (commits 481de7f / 75603f4); canonical producer at data/scripts/build_spike_perN.py (commit c5e377f). Doctrine-aligned (A21/A39/B13/B16/B18/E32/E32(e)/G22).

## Headline numbers — three resolutions

| Width | n_cells | Total $    | Capital     | ROI%   | Negative cells | Hold cells |
|-------|---------|------------|-------------|--------|----------------|------------|
| 1c    | 90      | +$2,029.20 | $26,819.70  | +7.57% | 21             | 7          |
| 2c    | 45      | +$1,501.80 | $26,819.70  | +5.60% | 11             | 1          |
| 3c    | 30      | +$1,137.40 | $26,819.70  | +4.24% | 8              | 1          |

## Daily framing

Average trading day: 48.86 N's, $246.05 capital deployed, $18.62 earnings → +7.57% per-N average ROI on cycling capital.

## Regime breakdown (1c resolution)

| Regime | Anchor range | Capital     | Total $   | ROI%    |
|--------|--------------|-------------|-----------|---------|
| Cheap  | 5–30c        | $2,299.20    | +$846.80  | +36.83% |
| Mid    | 31–65c       | $11,769.00    | +$741.30  | +6.30% |
| High   | 66–94c       | $12,751.50    | +$441.10  | +3.46% |

## Cross-category comparison

| Metric | ATP_MAIN | WTA_MAIN | ATP_CHALL (this run) |
|---|---|---|---|
| Total N | 4,137 | 3,683 | 5,326 |
| Trading days | 252 | 248 | 109 |
| 1c total $ | +$1,658.80 | +$1,824.90 | +$2,029.20 |
| 1c capital $ | $21,003.40 | $18,545.90 | $26,819.70 |
| 1c ROI | +7.90% | +9.84% | +7.57% |
| Cheap regime ROI | +36.13% | +43.22% | +36.83% |
| Mid regime ROI | +7.45% | +9.70% | +6.30% |
| High regime ROI | +3.11% | +3.52% | +3.46% |
| Hold cells (1c) | 8 | 10 | 7 |
| Negative cells (1c) | 15 | 14 | 21 |
| Avg N / trading day | 16.42 | 14.85 | 48.86 |
| Avg daily ROI | +7.90% | +9.84% | +7.57% |

## Deployment rule

Trade all 90 cells per the locked checklist (atp_chall_descriptive_1c.parquet). Same operational philosophy as ATP_MAIN/WTA_MAIN: volume is the constraint; Tier 3 marginal cells are execution-bound, not strategy-bound; Tier 4 (negative cells) is acceptable drag.

## Methodology

Identical to ATP_MAIN_LOCKED_DOWN.md methodology (commit 481de7f). 1c/2c/3c non-overlapping cells, hindsight-optimal per-cell exit-or-hold, capital = anchor_price × N × 10ct in dollars, ROI = best_sum / capital * 100. Spike per-N parquet built by canonical producer data/scripts/build_spike_perN.py (commit c5e377f); same producer reproduces ATP_MAIN and WTA_MAIN parquets byte-identical.

## Three-axis caveat

AXIS 1 — Exit-side fill realism (pushes DOWN). 0.4-0.8x of simulated, B25/Cat-11 evidence, pending Layer C.
AXIS 2 — Entry-side maker improvement (pushes UP). ~+10-30% on the headline, pending dedicated measurement. Tier 3 marginal cells are most levered to entry-side improvement.
AXIS 3 — Arrival frequency (G22). Frequency observable (48.86 N/day at 10ct); sizing depends on depth (F33).

## What this is NOT

- NOT a predictive rule (descriptive measurement only).
- NOT deployable dollars (three-axis caveat between this and realized PnL).
- NOT a single "correct" number — three resolutions are honest descriptions at three cell granularities.

## State after this commit

ATP_MAIN: LOCKED (commit 481de7f). WTA_MAIN: LOCKED (commit 75603f4). ATP_CHALL: LOCKED (this commit). WTA_CHALL: pending — same methodology to apply via the canonical producer.

