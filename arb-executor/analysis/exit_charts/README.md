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

```
python build_chart_pooled_gauge.py     # LAYER 2 -> chart_pooled_gauge.html (+ pooled_N_per_cell.csv)
```

## Conceptual corrections adopted (2026-05-31)

1. **No winner/loser split — reach is settlement-blind.** reach(c,X) = fraction of ALL
   contracts passing through c that ever trade to c+X. A contract that settles at 1¢ but
   traded through c+X earlier filled our resting sell = a real fill. Settlement enters
   ONLY on the misses: `net = reach·X − miss_rate·(c − 100·settle | miss)`.
   *(Layer 1 reach was already settlement-blind & traded-price; Layer 2 adds the net term.)*
2. **Reach instrument = TRADED price** `max(forward price_high) ≥ c+X` (skip-inclusive).
   `max_yes_bid_forward_*` are quoted bid → false-positive risk → banned for reach.
   **`bounce_*` is bid-derived** (corr **0.84** vs `max_yes_bid_forward` at settlement, 0.74
   vs traded; and goes negative) → not reused for reach either.
3. **Layer 2 — sand-pooled sample** (`build_chart_pooled_gauge.py`): every cell's reach/net/ROI
   is computed on the overlap-weighted neighbor pool, not own-cell N. Both raw-N and pooled-N
   reported.

### Schema flag-back — existing fields (check before imposing new bands)
| field | encodes | values (ATP_MAIN probe) |
|---|---|---|
| `regime` | match phase | premarket 23093 / in_match 4109 / settlement_zone 28 |
| `premarket_phase` | pregame sub-phase | stable 22141 / formation 952 / None 4137 |
| `spread_band` | liquidity | tight 15276 / medium 7739 / wide 4215 |
| `entry_band_lo/hi` | **price deciles** (0-10…90-100) | already a cost-basis banding by price (~75% concordant with per-minute round(100·yes_bid); the gap = it's anchored at a reference minute, not per-minute) |

→ **The proposed 5 cost-basis bands (5-20/21-40/…/81-94) reinvent `entry_band` at coarser
resolution.** Layer 2 therefore pools on the **continuous cell grid** and lets the shape
emerge; if a banding is wanted, reuse `entry_band` deciles rather than a conflicting 5-band scheme.

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

## Layer 2 — sand-pooled settlement-blind gauge (probe)

Pooling each cell through the sand overlap weights (k±3) thickens every cell's sample,
favorites included:

| denominator | raw (own-cell) | pooled (k±3) |
|---|---|---|
| minute-grains N | 31 – 1097 | **174 – 4497** |
| **distinct matches** (deployment-relevant) | 8 – 23 | **14 – 31** of 39 |

Thin favorites (c=81–94, raw 8–13 matches) rise to **17–20 matches**; thin deep underdogs
(c=8–14) to 25–31. The minute-N multiple (3–23×) is inflated by within-match autocorrelation
— **the distinct-match count is the honest denominator for any hit-rate gate.**

**Shape revealed (not pre-imposed):** optimal-net X folds monotonically from base to apex —
deep underdogs swing big (c=5 → +81, reach 47%, net +35¢; a miss costs ≤5¢), favorites take
small-certain (c=93 → +6, reach 100%, net +6¢; a miss costs ~93¢). The even line (c≈50) holds
the largest nets (c=53 → +46, net +40¢). This is the unified mirror-fold the gauge was meant
to surface.

> ⚠️ Deep-underdog extreme-X optima (c≤14, X≥70) ride a handful of comeback paths; reach there
> is path-autocorrelated. Do not deploy these until gated on **distinct-match** hit-rates
> (not minute-N). The 85% floor stays unlocked per instruction.

## Caveats for the full-universe re-run
- Edge/low-c cells are sparse on 38 games (drives sand mean down, creates off-diagonal optima).
- Entry = every minute (yes_bid_close always populated) → entry observations are autocorrelated
  within a ticker; this inflates N but not the per-cell fill estimate. Revisit weighting at scale.
- Forward window = to settlement. A capped-horizon variant is a one-line change in `compute_forward_max`.
