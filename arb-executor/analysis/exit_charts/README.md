# ATP_MAIN exit-strategy chart producers

Three reproducible, re-runnable producers for the ATP_MAIN exit strategy. All run on
the **38-game ATP_MAIN probe** by default and re-run on the full per-minute universe
by swapping `--input` (file / directory / glob) — nothing about the probe is hardcoded.

```
python build_chart_sand_overlap.py     # -> chart_sand_overlap.html
python build_chart_mirror_outlook.py   # -> chart_mirror_outlook.html
python build_chart_pyramid.py          # -> chart_pyramid.html (+ pyramid_blocks.csv)
# full universe, e.g.:
python build_chart_pyramid.py --input ../../data/durable/per_minute_universe/full --out pyramid_full.html
```

Shared data layer: `chart_common.py` (ONE cell definition, ONE reach engine).

> ⚠️ The spec referenced `arb-executor/analysis/CHART_DEFINITIONS_VERIFIED.md`, which
> **does not exist in the repo**. The instruments below are taken verbatim from the
> build prompt (which supersedes that file for the reach instrument anyway).

## Instrument contract

| Quantity | Instrument | Notes |
|---|---|---|
| **Cost-basis cell c** | `round(100 · yes_bid_close)` | the bid you lay & get filled at; same anchor as the project's `bounce_*` columns. Labels entry only. |
| **Reach / fill (CORRECTED)** | `max(forward price_high) ≥ (c+X)/100` | last-traded intraminute high; forward-max is **skip/gap-inclusive** (a print through c+X fills). 67% NaN minutes = genuine no-trade non-events, never patched. |
| **Sand overlap** | grain-mass (option b) | of c's minute-grains, fraction whose ticker also visits c±k. |
| **Mirror** | in-row `partner_yes_bid_close` | level-sum + excursion-window only. Never a timestamp join / minute-diff. PINNED — not re-derived. |

**Banned forward instruments** (each produced a false result on this project):
`yes_bid_high` (quote posted & pulled), `yes_bid_close` / `price_close` (close-of-minute
lag), `mid_close` (phantom midpoint). The OLD `yes_bid_high` instrument is computed
**only** for the corrected-vs-old comparison below.

## CORRECTED reach — probe results (price_high) vs OLD (yes_bid_high)

Probe: **39 tickers / 20 events**, 27,230 minute-rows, 25,881 entry-observations with a defined cell.

| Exit | Eligible cells | **Corrected** ≥50% | Old (yes_bid_high) ≥50% | Corrected mean fill | Old mean fill |
|---|---|---|---|---|---|
| +5c  | 90 | **88** | 88 | **0.967** | 0.926 |
| +10c | 85 | **80** | 77 | **0.899** | 0.849 |
| +15c | 80 | **73** | 67 | **0.847** | 0.766 |

**The old `yes_bid_high` headline was a false NEGATIVE, not a false positive.** At +10c the
corrected price_high fill is ≥ the old in **71/85 cells, lower in 0, equal in 14**; the old
quote instrument *understated* fill by up to **46.8pp** in a single cell. Reason: trades lift
the ask above a resting bid, so the forward-max *traded* price exceeds the forward-max *bid*.
The old "excursion+10 ≥ 50% in 85/90 cells" must be read as the wrong instrument; corrected
is **80/85 eligible cells** (cells 5–89; c≥90 cannot reach +10 under the 99 lock).

Fill rates are high because exits rest **to settlement**: of 39 tickers, 20 settle to 1.0
(winner crosses any target ≤ 99) and 19 to 0.0 — the standard winning-side reach.

## Sand / overlap — probe results

Interior (cells with ≥50 grains): median k=±1 overlap = **96.8%** (40/82 cells ≥97%),
decaying outward (k=±2 ≈ 86%, k=±3 ≈ 79%). Reproduces the pinned ~97–100% at the dense
interior; the all-cell mean (91.6%) is dragged only by sparse edge cells on 38 games.
**Neighbor-pooling at c±1 is legitimate** — the same physical paths recur from adjacent
sample points.

## Mirror — probe results

Level-sum (`paired_yes_bid_sum`) probe mean **0.957** vs pinned **0.974** ✓ (close). The
macro panel's excursion scatter is a **shape-check illustration only** (overlapping 60-min
per-minute windows ≠ the pinned discovery method); its raw corr (+0.39) is **not**
canonical and does not override the PINNED **+0.66 / 85%-within-2c**. Discovery is not re-run.

## Pyramid — probe results

4,455 blocks. Optima trace the predicted diagonal cleanly in favorite rows (c=60→94:
optimal X falls 29→5 monotonically) and push far-right (toward the 99 lock) in wide
underdog rows. **8 off-diagonal optima flagged** (magenta) — all in sparse low-c probe
cells; the full-universe re-run should collapse these. Objective is `argmax_X(fill × ROI-on-cost)`,
**not** max fill alone. Every optimal block surfaces its full variable stack on hover
(fill%, ROI-on-cost, miss/comeback, N, partner mirror-check) — never a single-number verdict.

## Caveats for the full-universe re-run
- Edge/low-c cells are sparse on 38 games (drives sand mean down, creates off-diagonal optima).
- Entry = every minute (yes_bid_close always populated) → entry observations are autocorrelated
  within a ticker; this inflates N but not the per-cell fill estimate. Revisit weighting at scale.
- Forward window = to settlement. A capped-horizon variant is a one-line change in `compute_forward_max`.
