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

### Optimal-X objective — PREDICTABILITY-GATED (not argmax-net)

argmax(net) chases the cheap-cell moonshot — c5 → +81 at 47% reach nets +35¢ only because a
miss costs ~5¢. That variance-chase is rejected. The optimum is now:

> **optimal X = the deepest X whose pooled reach ≥ floor** (on the monotone reach envelope, so
> it never jumps a sub-floor dip to grab the 99-lock spike). Raw net stays as a visible compare
> layer only — never optimised on.

**Floor locked at 0.85** from the sweep (on healthy-pooled-N cells): 0.80 is unstable
(mean|ΔX| spike at the 0.80→0.81 step) and lets c5 creep to +17; 0.90 over-clamps the even
line (c50 +20→+7 off a reach cliff past 0.88). 0.85 sits mid-plateau. At 0.85, **c5 → +14
(89% reach, 280% ROI)** — the moonshot is gone and the fold is the *predictable* shape.

### Minute- vs match-weighted reach (the honest denominator)

Minute-weighted pooled reach over-counts winner-minutes (a winner lingers near c on its way up
and reaches 99). So a few deep mid-cell picks look predictable but aren't: **c53 → +46 reads
94% minute-weighted but only 68% match-weighted**; c21 → +34 reads 86% / 56%. These are
**flagged amber on the chart and `<<MATCH-UNCONFIRMED` in the report** (27/90 cells). The gauge
exposes them; it does not hide or deploy them.

- **`--gate-basis match` (DEFAULT — canonical deploy gate):** one match one vote. Result:
  **c5 → +13 (86% match reach, +10.3¢ expected return, 27 matches), c21 → +15, c53 → +12**,
  no moonshot, no 99-magnet. **1/90 cells thin** (matchN<15) on the probe.
- `--gate-basis minute` (DIAGNOSTIC ONLY — do not deploy): over-optimistic wherever winners
  loiter. The minute−match gap per cell maps the winner-contaminated cells (c53 +9pp, c21 +10pp)
  — useful info, never a deploy basis.

Why minute-weighted is rigged: a winning contract loiters at a price on its way up to 99 and
donates dozens of "reached" minutes — ballot-box stuffing. Match-weighted asks the only question
that matters for deployment: of N distinct matches, how many actually paid. Confirmed over-optimistic
in 41/90 cells (e.g. c53 +46 reads 94% minute / 68% match; c40 +26 reads 85% / 55%).

**Deploy surface color = expected return** `= reach_match·X − miss_rate·(c−settle)` (cents), NOT
ROI-on-cost-when-hit — so cheap cells don't look 2× better than they deploy. **Per-cell match-N
shown** in hover; thin picks (<15 matches) flagged magenta.

### One match one vote (event-dedup — guard against side double-counting)

A tennis match has TWO sides (tickers). Counting per-side double-counts a single match wherever
**both** sides pass through a cell — validated on the full universe at **~1.5× near c≈50** (both
sides hover mid-range as the lead swings), tapering to ~1.0× at the extremes. So the canonical
denominator dedups to distinct **matches (event_ticker)**: each side gives a 0/1 reach outcome,
**averaged within the match to one vote in [0,1]**. Unbiased, no inflation, and `match_N` =
distinct matches (not sides). This is what prevents the winner-contamination from sneaking back
via the pairing. Memory-safe loader (`NEEDED_COLUMNS` projection + category filter pushdown)
keeps the 9.3M-row universe from ever fully materialising.

**Shape revealed (not pre-imposed):** a monotone fold — deep underdogs take a moderate deep
offset on their cheap basis (c5 → +13/+14, ~240–280% ROI), the even line takes the largest
predictable offsets, favorites take small-certain (c93 → +6, ~100% reach). The mirror-fold the
gauge was meant to surface — now on the predictable, not the moonshot, optimum.

## FULL-UNIVERSE results (2026-05-31) — match-weighted, 2,631 ATP_MAIN matches

Ran the match-gated gauge on the already-built full universe (`per_minute_features.parquet`,
9.33M rows, window 2025-06-18→2026-05-01) on the VPS, headless+frugal, peak RSS 1.18 GB, ~30 s.
Outputs: `chart_pooled_gauge_full.html`, `*_full.csv`.

- **Match-N firmed up everywhere:** per-cell pooled distinct-match-N **1,886–2,585** (of 2,631);
  raw own-cell **1,494–3,727**. **0/90 thin** (probe was 14–31 with 1 thin). Even favorites — which
  we expected to stay structurally thin — carry ~2,300+ pooled matches.
- **Side double-count killed (guard 2 confirmed):** minute−match gap collapsed to mean **−2.1 pp**
  (range −8.3…+3.5), only 11/90 cells >±5 pp. On the probe the per-side count inflated mid-cells
  to +7…+11 pp; one-match-one-vote removed it. Distinct matches **2,631 / 5,261 sides** (clean 2:1).
- **Shape — the probe's deep-underdog MOONSHOT was the illusion, NOT the engine.** The dead part is
  c5's +81: honest full-N is a **shallow reliable +4/+5 at 85–88%** — the predictable-bounce engine.
  The exit-OFFSET X rises with cost basis (deep-ud +4/+5, even +13, slight-fav +20), clipped at the
  top by the 99 lock; reach pins at the 0.85 floor; bands uniform.
- **DEPLOY metric = RETURN-ON-CAPITAL (exp_ret / c), not cents/trade.** Capital is the binding
  constraint, so cents/trade flatters favorites that tie up 80–93¢ to earn them. On return-on-capital
  the **deep-underdog engine dominates (~7× favorites)** — this CONFIRMS the engine (LESSONS A39),
  it does not reverse it:

  | rank | cell | exit | match reach | cents/trade | **ROC** | matchN |
  |---|---|---|---|---|---|---|
  | 1 | c5 | +4 | 88% | +2.8¢ | **55.7%** | 2547 |
  | 2 | c6 | +5 | 85% | +3.3¢ | **55.1%** | 2559 |
  | 3 | c7 | +5 | 85% | +3.2¢ | **46.2%** | 2580 |
  | … | … | | | | | |
  | low | c83 | +16 | 90% | +6.6¢ | **8.0%** | 2433 |
  | low | c90 | +5 | 97% | +4.4¢ | **4.8%** | 2400 |

  Band mean ROC: deep-ud **26.1%**, slight-ud 7.3%, even 6.4%, slight-fav 8.5%, heavy-fav 5.9%.
  Primary deploy-surface color is now ROC; cents/trade is a secondary toggle layer.
- Mirror was NOT re-run (pinned). HTML rendered locally from the pulled blocks CSV (plotly optional
  on the VPS; `render_from_blocks`). **Caveat:** peak RSS 1.18 GB > the <200 MB target — the parquet
  category filter didn't prune row groups, so 9.3M rows materialised transiently before downcast; it
  fit (1.4 GB avail + swap) and finished in 30 s without starving the trader, but a true chunked
  row-group read is the follow-up for strict <200 MB.

## ALL FOUR CATEGORIES (2026-05-31) — same locked method, run-only on full universe

Ran WTA_MAIN / ATP_CHALL / WTA_CHALL through the identical pipeline (settlement-blind traded
price_high reach, sand-pooled k±3, match-weighted one-match-one-vote gate, 0.85 floor, ROC deploy).
Headless+frugal on the VPS, nice'd, isolated scratch — peaked ~1.18 GB/run and ran slow under the
box's memory pressure (load → 3.2, nice kept the trader CPU-priority); disk held at 3.8 GB free.

| category | matches | sides | 2:1? | window | no-trade % | mid-cell side-infl | gap (killed?) | match-N range | top ROC | deep-ud / fav ROC |
|---|---|---|---|---|---|---|---|---|---|---|
| ATP_MAIN | 2,631 | 5,261 | ✓ 2.00 | Jun25–May26 | 67% | 1.46× | −0.3pp ✓ | 1,886–2,585 | c5 **56%** | 26.1 / 5.9 = **4.4×** |
| WTA_MAIN | 2,520 | 5,040 | ✓ 2.00 | Jun25–Apr26 | **72%** | 1.46× | −1.2pp ✓ | 1,822–2,492 | c5 38% | 21.7 / 4.5 = 4.8× |
| ATP_CHALL | 3,804 | 7,608 | ✓ 2.00 | Jan26–May26 | **58%** | 1.46× | +0.2pp ✓ | 2,608–3,747 | c5 50% | 21.1 / 4.7 = 4.5× |
| WTA_CHALL | 649 | 1,298 | ✓ 2.00 | Jan26–May26 | 56% | 1.50× | −0.9pp ✓ | **431–640** | c5 38% | 15.0 / 4.2 = 3.6× |

**Validations confirmed per category (not assumed from ATP):**
- **2:1 sides:matches** holds exactly in all four (mean 2.00, zero matches with ≠2 sides).
- **c≤50 side double-count is real in every category** (mid-cell sides/matches ~1.5×, ~1.0× at
  extremes) and the match-weighted gate **kills it everywhere** — minute−match gap collapses to
  −1.2…+0.2 pp at mid-cells (vs the +7…+11 pp it would be on per-side counting).

**Findings (reported as findings, not bugs):**
1. **Deep-underdog ROC engine repeats in all four** (concentration 3.6–4.8×, top cell always c5).
   The fold holds: deep-ud exits +3–6, even +8–17, favorites lock-clipped; reach pinned ~87%; bands
   uniform. The structure is category-invariant.
2. **ATP_MAIN runs HOTTEST, not WTA — opposite of the "WTA runs hotter" prior.** On return-on-capital
   ATP_MAIN c5=56% / deep-ud 26% beats WTA_MAIN c5=38% / 21.7% (same exit depth, but WTA underdogs
   bounce *less*: c5 exp-ret +1.9¢ vs ATP +2.8¢). Flagging the contradiction with the prior.
3. **Challenger surfaces rest on MORE real prints, not fewer:** no-trade 56–58% vs Mains' 67–72%.
   WTA_MAIN is the thinnest-printing surface (72% no-trade). ATP_CHALL has the **most matches** (3,804)
   and densest prints — Challenger liquidity is not the weak point.
4. **Thinnest cells are EVEN-MONEY (c44–50), not the favorite tail** — cost basis is bimodal
   (fav/underdog) with a trough at even money; favorites stay well-populated (winners traverse the
   tail to settlement). So the operator's expected favorite-tail thinness did **not** materialise.
5. **No category has a statistically thin cell.** Smallest is WTA_CHALL (649 matches) whose thinnest
   cell still carries **431 pooled matches** (~±3% CI on an 85% rate) — fine. WTA_CHALL is ~5× smaller
   and spans only ~3 months (Jan29–May1; Challenger collection started late), so treat its magnitudes
   as provisional, but the shape is the same.

Outputs per category: `deploy_gated_optima_<CAT>.csv`, `pooled_gauge_blocks_<CAT>.csv`,
`chart_pooled_gauge_<CAT>.html`. Mirror not re-run (pinned). `validate_category.py` is the
per-category validation pass.

## ENTRY maker-fill surface (Axis 2) — premarket tape, all 4 categories (2026-05-31)

`build_chart_entry_fill.py` on `premarket_tape_v1.parquet` (T-4h→T-20m, 2.06M rows, sha ff2a63d9).
Entry-side mirror of the exit ROC surface; supersedes Path B v4. Rest a maker BUY at cell c during
premarket; **fill = a real traded low ≤ bid before T-20m** (`min(forward price_low) ≤ bid/100`) —
the honest cross DOWN into the bid, NOT the quoted-ask-comes-down phantom Path B counted. Per-cent,
per-minute placement, cluster-sand-pooled, one-match-one-vote. A maker fill (0 fees, bought at bid)
lands a cost basis below the taker baseline → lifts that position's exit ROC.

Headline = place at the first premarket minute price is at c, rest to T-20. Base bid at c plus
conservative variants 1–2¢ below (fills only on a genuine dip). Per-cell × per-placement-minute
heatmap shows fill-prob growing the earlier you place.

| category | premarket rows | matches | c5 fill @c / @c−2 | mid–fav fill @c | WAIT/90 | CHASE/PASS cells |
|---|---|---|---|---|---|---|
| ATP_MAIN | 704k | 2,488 | 46% / **29%** | 65–72% | 86 | **c5,6,7,8** |
| WTA_MAIN | 614k | 2,366 | 52% / 37% | 66–71% | 90 | none |
| ATP_CHALL | 643k | 3,550 | 48% / 30% | 56–69% | 88 | c5,6 |
| WTA_CHALL | 103k | 589 | 56% / 35% | 58–70% | 90 | none |

**The tension is real and quantified (and tour-specific):**
- **Cheap cells = highest exit ROC but hardest to maker-fill.** ATP_MAIN c5: exit ROC **56%** but
  entry fill only **46% @c / 29% @c−2** → flagged **CHASE/PASS** (take the taker; the drift rarely
  comes down to a 5¢ bid). The richest exit cells are the hardest to fill cheap.
- **ATP runs hot-but-hard, WTA runs cool-but-easy.** ATP (higher ROC) flags its 2–4 cheapest cells
  CHASE/PASS; **WTA fills easier everywhere (c5 52–56% @c)** and says WAIT on all 90 despite lower ROC.
  The chase-vs-wait call differs by tour — the surface makes it per-cell explicit.
- Shape direction matches the sanity prior (cheap lowest, rising); the **conservative c−2 bid is where
  the ~30% cheap-cell fill shows up** (anchor @c is higher because price is already at c). Offsets
  correctly monotone (fill@c ≥ @c−1 ≥ @c−2 — a dip to c−2 implies passing c).

Outputs per category: `deploy_entry_fill_<CAT>.csv` (per-cell headline + verdict + cost basis),
`entry_placement_surface_<CAT>.csv` (c × placement-minute), `chart_entry_fill_<CAT>.html`.
Premarket coverage is ~5% fewer matches than the exit universe (some matches lack premarket tape).

## Premarket DIRECTIONAL-DRIFT hypothesis test — full universe, 4 categories (2026-06-01)

`premarket_drift.py` on `premarket_tape_v1.parquet`. Thesis tested: favorites (high cells) drift UP
and underdogs (low cells) drift DOWN over T-4h→T-20 (retail piles into the favorite). drift =
traded price near T-20 − traded price near T-4h (price_close, real prints only), grouped by starting
band, split by eventual outcome.

**HEADLINE THESIS: REJECTED at full N.** Mean band drifts are all small (<±1¢) and inconsistent in
sign across categories; %up≈%down (34–54%). **Heavy-favorites drift slightly DOWN in all four**
(−0.97 / −0.35 / −0.19 / −0.27), the opposite of the thesis. The probe's apparent favorite-up/
dog-down pattern was small-sample noise. There is no systematic premarket directional push.

**THE OUTCOME SPLIT is decisive — it's efficient repricing, NOT retail overshoot:**

| band | ATP_MAIN W/L drift | WTA_MAIN | ATP_CHALL | WTA_CHALL | verdict (all cats) |
|---|---|---|---|---|---|
| deep-ud | +6.0 / +0.2 | +1.2 / −0.5 | +1.6 / −0.4 | +0.3 / −1.2 | **repricing** |
| slight-ud | +1.7 / −1.4 | +3.9 / −0.5 | +1.4 / −1.4 | +1.8 / −2.3 | **repricing** |
| slight-fav | +1.8 / −1.8 | +1.4 / −3.6 | +1.4 / −1.1 | +1.9 / −2.7 | **repricing** |
| heavy-fav | −0.2 / −5.4 | −0.3 / −0.7 | +0.6 / −4.5 | +0.4 / −4.1 | **repricing** |

Eventual **winners drift up, losers drift down — in every band**. The overshoot test (does the
outcome-contrary group drift in the retail direction?): **favorite-LOSERS drift DOWN** (−4 to −5¢,
not up) and **underdog-WINNERS drift UP** (+1.4 to +6¢, not down) everywhere. So the market correctly
marks premarket toward the true result. **No tradeable overshoot in any band or category** —
you can't ride/fade it because the drift just encodes the outcome you don't yet know.

**Timing:** drifts are small and gradual; nothing concentrates in the last 30 min. No timing edge.

**Mirror: CONFIRMED** (corr(underdog-drift, favorite-drift) = −0.80…−0.90, mean(driftA+driftB) ≈ 0
[+0.06…+0.41¢], 65–77% within 2¢ of perfect mirror). The two sides ARE one mirrored position — but
it mirrors *efficient repricing*, so it confirms structure (level-sum complementarity in motion), not
an exploitable two-sided edge.

**Playbook consequence:** there is **no directional entry-timing edge** — "buy the favorite early
before the push" has no push to front-run. Chase-vs-wait therefore stays **fill-probability-only**
(the entry maker-fill surface above): rest the bid where the maker fill is likely, take the taker
where it isn't. No directional overlay. A clean, money-saving negative result. Per-band CSVs:
`premarket_drift_<CAT>.csv`.

## ENTRY BID-DEPTH optimizer — harvest the premarket dip (2026-06-01)

`build_chart_entry_depth.py` joins three locked pieces to answer "how far below anchor to lay the
maker bid": (1) honest dip→fill curve p(c,D) = traded low ≤ (c−D)/100 before T-20m, depth-swept
0–12, cluster-sand-pooled, one-match-one-vote; (2) the locked exit ROC per cost cell; (3) optimal
depth. NOT directional (that was rejected) — it harvests the reliable below-anchor oscillation found
by the drift-envelope (`drift_envelope_*_2026-05-26.md`: median ~3¢ bid-dip, ~97% dip below anchor).

Two depths per anchor cell:
- **reliable depth (headline)** = max-ROC-lift depth whose HONEST fill ≥ 40%, falling back to D=0
  (no dip) where dipping doesn't lift ROC. The dip you can actually rest into.
- **aggressive argmax** = unconstrained argmax p·(ROC(c−D)−ROC(c)); flagged when pinned at DMAX=12
  (the deep-underdog ROC gradient pulls past the cap at 17–29% fill — speculative low-fill tail).

**Findings (all 4 categories):**
- **The dip-harvest lift is real but MODEST and concentrated in the low-cell band.** Reliable-depth
  ROC lift by band (mean): **deep-ud +1.7…+2.8pp**, slight-ud +0.7…+0.9pp, even/fav **+0.1…+0.4pp**.
  Dipping a few cents toward the deep-underdog engine is where it pays; for even/favorite cells the
  exit ROC is flat across neighbours so a cheaper basis barely lifts. ~28–43 of 90 cells show any
  positive lift; the rest lay at the anchor (D=0).
- **The richest cell (c5) has NO dip room** (already at the 5¢ floor → D=0). You can't harvest below
  the floor, so the top-ROC cell is taken at anchor.
- **Honest traded fill at the reliable dip is ~40–46%** — far below the envelope's bid-based "97% dip
  / median 3¢". The quoted-bid dip **overstates** maker fillability; a real trade comes down to a
  2–5¢ dip only ~40% of the time. (Instrument distinction; the bid-based env median is carried as a
  cross-check column, not the gate.)
- WTA harvests slightly more than ATP (deep-ud +2.4/+2.8 vs +1.7) — consistent with WTA's easier fills.

**Net:** the entry→exit lifted picture is a **small, low-cell-concentrated ROC bump on top of the
exit engine**, not a new edge — consistent with the efficient-premarket drift result. Deploy: lay
the maker bid a few cents below anchor in the underdog band (reliable_depth), take at anchor elsewhere.
Outputs: `deploy_entry_depth_<CAT>.csv` (reliable + aggressive + cost basis + combined ROC + env
cross-check), `entry_depth_fill_<CAT>.csv` (full c×D fill surface), `chart_entry_depth_<CAT>.html`.

## Caveats for the full-universe re-run
- Edge/low-c cells are sparse on 38 games (drives sand mean down, creates off-diagonal optima).
- Entry = every minute (yes_bid_close always populated) → entry observations are autocorrelated
  within a ticker; this inflates N but not the per-cell fill estimate. Revisit weighting at scale.
- Forward window = to settlement. A capped-horizon variant is a one-line change in `compute_forward_max`.
