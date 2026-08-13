# The macro journey table — station-to-station, no hourly medians [ANALYTICAL_ESTIMATE · UNVALIDATED-CANDIDATE]

Analysis seat only. Read-only. **Corrects the scope-defective theta table @ `2d48e4ee`** — that table is
restamped **SCOPE-DEFECTIVE-FOR-MACRO** in the palantír and retained only as its one honest result (no hourly
escalator exists). This table measures the **journey**: per leg, all 804 games, three stations —
**window-open price → onset price → window-edge price**. Stations stated: open = first in-window mid; onset =
mid at the leg's interim onset (`22441e05`); **edge = last in-window mid** (the stated choice; the last true
trade is carried per row as reference, not the station). Cells classify by the **journey's origin**
(open-price region) so movers aren't clipped. No hourly medians anywhere. Machine table + all 1,602 rows:
`MACRO_JOURNEY_TABLE.json`.

## Burst concentration — the step-not-gradient proof

Share of each leg's **total absolute travel occurring in its top-3 hours**:

**p10 0.533 · p25 0.687 · median 0.814 · p75 0.916 · p90 0.978** (n = 1,602).

The median leg does **81% of its whole window's price travel in three hours**; a tenth of legs do ~98% of it
in three hours. There is no gradient — there are steps. (This is also the post-mortem of the theta table:
hourly medians read 0 because most hours ARE 0; the journey happens in bursts the median hour never sees.)
Per-cell burst tables in the JSON.

## The journeys, signed, by category × origin region (headline cells; full 16-cell grids in the JSON)

**Net displacement open→edge** — the movers live in the 26_50 origin band:

| cell (origin) | n | p10 | p25 | med | p75 | p90 |
|---|--:|--:|--:|--:|--:|--:|
| ATP_CHALL \| 26_50 | 559 | **−32.5** | −12.5 | 0.0 | +16.0 | **+34.0** |
| ATP_CHALL \| 51_75 | 114 | −6.5 | −1.0 | +1.0 | +3.5 | +8.0 |
| ATP_CHALL \| ge76 | 26 | −0.5 | +0.5 | +2.0 | +3.0 | +7.0 |
| ATP_CHALL \| le25 | 37 | −4.0 | −2.5 | −1.0 | +2.5 | +8.5 |

A leg that opens mid-band (26_50) is a coin-flip mover with ±33¢ decile tails; legs opening in the wings
barely travel. Medians ≈ 0 everywhere — displacement is two-sided and symmetric; the information is in the
tails, which is why origin-classification (not close-classification) was ordered and matters.

**The firming leg (open→onset) vs the awake leg (onset→edge)** — where the journey actually happens
(ATP_CHALL|26_50, the mover cell): firming p10/p90 = **−23.0 / +28.5**; awake p10/p90 = **−14.0 / +10.5**.
**The larger share of a mover's displacement is complete before onset** — the formation era does the heavy
repricing; the awake market still carries real ±10–14¢ decile tails (the part a licensed rest can lawfully
meet). Same shape in the other categories at smaller amplitude; full grids in the JSON.

## The pair view — the two legs jointly (801 games with both legs scored)

| joint class | games |
|---|--:|
| **MIRRORED** (nets opposed, sum within 5¢) | **547 (68.3%)** |
| FLAT_BOTH (both |net| < 5¢) | 196 (24.5%) |
| OPPOSED_UNBALANCED (opposed, sum > 5¢) | 37 (4.6%) |
| **DECOUPLED_SAME_DIRECTION** | **21 (2.6%)** |

The pair constraint holds at journey grain: two-thirds of games are clean mirrors, a quarter never move, and
genuine same-direction decoupling is a 2.6% event — the substrate coupling parts 1/3/4 will quantify finer.

## Conservation

1,602 legs scored of 1,608 (6 no-tape/short, named); 1,563 with an onset station (legs without onset carry
open→edge only); pair view 547+196+37+21 = 801 games + incomplete-tape remainder; every distribution signed;
origin cells sum to their categories. **UNVALIDATED-CANDIDATE** — enters the palantír as G4 with provenance
triple; no decision-input claims; wiring only after its own proving-loop iteration, prior-not-gate.
ANALYTICAL_ESTIMATE.
