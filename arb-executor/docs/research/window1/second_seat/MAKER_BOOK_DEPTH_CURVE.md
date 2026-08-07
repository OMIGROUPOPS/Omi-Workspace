# The maker book + depth curve — the drift thesis priced

Analysis seat only. Read-only. Built on sealed artifacts (near-miss `65d49b5d`,
REST_SANITY `4c52b6bf`, census case `9051d4de`, V36 ledger `bfde0d8`); **nothing sealed
was refit** — the depth curve is a fresh tape+prints measurement. Machine artifact:
`.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/MAKER_BOOK_DEPTH_CURVE.json`.

## (1) The honest maker book — census re-based, invalid conversions dropped

Dropping the 71 buyer-aggressed + 49 one-cent-rule-violating conversions removes **89
pairs** (some pairs carried more than one flag), leaving **459 honest pairs**.

| | value |
|---|--:|
| pairs | **459** |
| margin (p25 / median / p75) | 1 / **2** / 3 ¢ |
| gross total | 2,060¢ |
| **maker-only $ (zero fee)** | **$20.60 · 1-lot · $103.00 · 5-lot · $515.00 · 25-lot** |
| frontier ≤93 / ≤95 / ≤97 / <100 | 51 / 73 / 147 / 459 |

By category: ATP_CHALL 198 pairs ($6.99) · ATP_MAIN 99 ($5.63) · WTA_MAIN 97 ($5.99) ·
WTA_CHALL 65 ($1.99). By bell: exact 127 · live_by 251 · schedule 48 · clean 21 ·
contradictory 12. **The whole honest maker book is worth ~$20 at 1 lot / ~$515 at 25 lot.**

## (2) The depth curve — the thesis dial (k = 1,2,3,5,8)

Living rest generalized to `rest = min(best_bid − k, 99)`, tracked continuously; a
**level-touched fill** = a seller-aggressed print ≥5 lots landed at-or-through the rest
(queue-independent). Pair coupling is **lazy-leg-1**: each leg vs its OWN walked path, no
sibling accounting.

| k | legs filled | pairs <100 | **margin / fill** | **gross book $** |
|--:|--:|--:|--:|--:|
| **1** | **412** | **106** | 4.86¢ | **$20.03** |
| 2 | 226 | 59 | 6.81¢ | $15.39 |
| 3 | 166 | 48 | 7.98¢ | $13.25 |
| 5 | 114 | 37 | 10.28¢ | $11.72 |
| 8 | 86 | 27 | 11.64¢ | $10.01 |

**The drift thesis, priced:** margin-per-fill **does** rise with depth (4.86 → 11.64¢ —
the drift is real, a deeper rest earns a better price on each fill). **But book value
falls monotonically** ($20.03 → $10.01) because the fill count decays faster than the
margin grows — far fewer sellers reach 8¢ under the bid than 1¢ under it. **k = 1 maximizes
book value in every category.**

**The category law** (no cross-category aggregation; min-n=30 per cell): best k = 1
everywhere, but evidence quality splits —

| category | best k | k=1 book $ | evidence |
|---|--:|--:|---|
| ATP_CHALL | 1 | $9.71 | **native n≥30** (46 pairs) |
| ATP_MAIN | 1 | $4.80 | **native n≥30** (32 pairs) |
| WTA_CHALL | 1 | $3.05 | **POOLED** (11 pairs < 30) |
| WTA_MAIN | 1 | $2.47 | **POOLED** (17 pairs < 30) |

The two ATP cells stand on native n; the two WTA cells are under min-n and must be
**hierarchically pooled to their category-tour parent** (per the June blending law) before
any live claim — the WTA best-k=1 call is provisional. At every k ≥ 2, *no* category cell
has native n ≥ 30 (all ≤27 pairs) — the deep book is un-provable at cell level.

*(Touch-verified k=1 = 106 pairs / $20.03 vs the census-conversion honest book 459 pairs /
$20.60: 4× fewer pairs, the **same dollars** — the census's extra pairs are razor-thin, so
the maker book's real ceiling is ~$20/1-lot on either count.)*

## (3) Sweep interaction — the decay is buffered, not erased

Of **1,587** seller-hit sweeps (≥5-lot strict-law recut of REST_SANITY's 1,787), the share
whose price span reaches depth k — a rest k-under the sweep top fills on the *same* flow:

| depth k | sweeps reaching | share |
|--:|--:|--:|
| 1 | 1,587 | 100% |
| 2 | 1,587 | 100% |
| 3 | 1,210 | 76.2% |
| 5 | 743 | 46.8% |
| 8 | 318 | 20.0% |

Sweeps **do** carry deeper rests — 76% of them fill a k=3 rest, 47% a k=5 — so the
depth-fill decay is *flatter than isolated prints imply*. But the tail of fills is
dominated by single prints, not sweeps, so total fills still fall 412→166→86. The sweep
buffer softens the curve; it does not invert it.

## (4) Pilot spec — maker-only

- **Measure, per category × k:** count seller prints ≥5 lots landing **at-or-through** our
  standing `best_bid − k` (level touches) vs **actual fills** after queue = **queue yield**;
  conversion = fills / touches.
- **Reads:** require **≥30 completed games AND ≥200 armed levels** per category before any
  ruling. Cells under min-n are **POOLED** to the category-tour parent, evidence downgraded.
- **Kill number per k:** refute depth k in a category if the observed queue-yield ×
  margin-per-fill(k) falls **below the proven book value of k = 1** — since the curve is
  monotone decreasing in book value, any k ≥ 2 is refuted the moment it fails to beat k = 1,
  which the historical tape already says it cannot. **Maker fees are zero, so there is no
  fee floor — the kill is purely fill-yield vs the k=1 baseline.**
- **Best k per category (fees zero):** **k = 1 for all four** — ATP_CHALL ($9.71) and
  ATP_MAIN ($4.80) on native n; WTA_CHALL ($3.05) and WTA_MAIN ($2.47) **pooled, provisional**.

## Verdict

Priced, the drift thesis is **half true and net-negative for the book**: deeper rests do
earn more per fill (4.86→11.64¢) and sweeps carry them (76% reach k=3), but the fill-count
collapse dominates — **shallow k=1 tracking is the optimal maker book in every category**,
worth **~$20 at 1-lot / ~$515 at 25-lot**, with only the two ATP cells on native evidence.

## Conservation

1,608 legs scanned. Honest maker book 459 pairs (548 census − 89 flagged). Depth curve
legs filled 412/226/166/114/86 at k=1/2/3/5/8; pairs<100 106/59/48/37/27; gross
$20.03/15.39/13.25/11.72/10.01. Sweeps 1,587 (≥5-lot recut); reach 1587/1587/1210/743/318.
Best k=1 all categories (ATP native, WTA pooled).
